
from werkzeug.datastructures import FileStorage
import time
from flask_restx import Resource, Api, marshal
from flask_cors import CORS
from flask import Flask, request, jsonify
from pathlib import Path
import json
import threading

from models.models import get_models
from tools.logger import setup_logger
from tools.network import network_monitor

import sys
import os
# Allows Python to find package from sibling directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from algo.algorithms.algo import MazeSolver  # nopep8
from algo.tools.commands import CommandGenerator  # nopep8
from image_rec.model import load_model, predict_image, predict_image_t2, stitch_image  # nopep8

app = Flask(__name__)

api = Api(app, validate=True)
restx_models = get_models(api
                          )
logger = setup_logger()

CORS(app)

# load model for image recognition
model = load_model()  # Default model

# poll wi-fi SSID to check that RPI can connect to API server
# TODO remove if this causes any performance issues or bugs
# threading.Thread(target=network_monitor, args=(logger,), daemon=True).start()


@api.route('/status')
class Status(Resource):
    @api.response(model=restx_models["Ok"], code=200, description="Success")
    def get(self):
        """
        To check if the server is running
        """
        return marshal(
            {
                "result": "ok"
            },
            restx_models["Ok"]
        ), 200


@app.after_request
def log_response_info(response):
    ignored_paths = ["/swaggerui/", "/swagger.json",
                     "/swagger/", "/static/", "/favicon.ico"]
    # Only log responses for requests to API endpoints, ignoring Swagger-related requests
    if not any(request.path.startswith(path) for path in ignored_paths) and request.path != "/":
        try:
            logger.debug(json.loads(response.data))
        except json.JSONDecodeError:
            logger.debug("Response data is not valid JSON.")
    return response


@api.route('/path')
class PathFinding(Resource):
    @api.expect(restx_models["PathFindingRequest"])
    @api.response(model=restx_models["PathFindingResponse"], code=200, description="Success")
    @api.response(model=restx_models["Error"], code=500, description="Internal Server Error")
    def post(self):
        """
        For RPI to request pathfinding algorithm
        """
        try:
            # Get the json data from the request
            content = request.json
            logger.debug("Request received from client:")
            logger.debug(f"{content}")

            # Get the obstacles, retrying, robot_x, robot_y, and robot_direction from the json data
            obstacles = content['obstacles']
            # TODO: use alternative algo for retrying?
            retrying = content.get('retrying', False)
            robot_x, robot_y = content.get(
                'robot_x', 1), content.get('robot_y', 1)
            robot_direction = content.get('robot_dir', 0)

            optimal_path, commands = None, None

            # Initialize MazeSolver object with robot size of 20x20, bottom left corner of robot at (1,1), facing north.
            maze_solver = MazeSolver(size_x=20, size_y=20, robot_x=robot_x,
                                     robot_y=robot_y, robot_direction=robot_direction)

            # Add each obstacle into the MazeSolver. Each obstacle is defined by its x,y positions, its direction, and its id
            for ob in obstacles:
                maze_solver.add_obstacle(ob['x'], ob['y'], ob['d'], ob['id'])

            start = time.time()
            # Get shortest path
            optimal_path, cost = maze_solver.get_optimal_path()
            runtime = time.time() - start
            logger.debug(
                f"Time taken to find shortest path using A* search: {runtime}s")
            logger.debug(f"cost to travel: {cost} units")

            # Based on the shortest path, generate commands for the robot
            motions, obstacle_id_with_signals, scanned_obstacles = maze_solver.optimal_path_to_motion_path(
                optimal_path)
            command_generator = CommandGenerator()
            commands = command_generator.generate_commands(
                motions, obstacle_id_with_signals, scanned_obstacles, optimal_path)
            logger.debug(
                f"Number of obstacles scanned: {len(scanned_obstacles)} / {len(obstacles)}")

            # Get the starting location and add it to path_results
            path_results = []
            for pos in optimal_path:
                path_results.append(pos.get_dict())

            return marshal(
                {
                    "data": {
                        'path': path_results,
                        'commands': commands,
                    }
                },
                restx_models["PathFindingResponse"]
            ), 200
        except Exception as error:
            logger.debug("", exc_info=True)
            return marshal(
                {
                    "error": repr(error)
                },
                restx_models["Error"]
            ), 500


# FOR SIMULATOR TESTING ONLY
@api.route('/simulator_path')
class SimulatorPathFinding(Resource):
    @api.expect(restx_models["SimulatorPathFindingRequest"])
    @api.response(model=restx_models["SimulatorPathFindingResponse"], code=200, description="Success")
    @api.response(model=restx_models["Error"], code=500, description="Internal Server Error")
    def post(self):
        """
        FOR SIMULATOR TESTING ONLY. RPI SHOULD NOT BE USING THIS ENDPOINT
        """
        try:
            # Get the json data from the request
            content = request.json
            logger.debug("Request received from client:")
            logger.debug(f"{content}\n")

            # Get the obstacles, retrying, robot_x, robot_y, and robot_direction from the json data
            obstacles = content['obstacles']
            # TODO: use alternative algo for retrying?
            retrying = content.get('retrying', False)
            robot_x, robot_y = content.get(
                'robot_x', 1), content.get('robot_y', 1)
            robot_direction = content.get('robot_dir', 0)
            num_runs = content.get('num_runs', 1)  # for testing

            optimal_path, commands, total_cost, total_runtime, = None, None, 0, 0
            for _ in range(num_runs):
                # Initialize MazeSolver object with robot size of 20x20, bottom left corner of robot at (1,1), facing north.
                maze_solver = MazeSolver(size_x=20, size_y=20, robot_x=robot_x,
                                         robot_y=robot_y, robot_direction=robot_direction)
                # Add each obstacle into the MazeSolver. Each obstacle is defined by its x,y positions, its direction, and its id
                for ob in obstacles:
                    maze_solver.add_obstacle(
                        ob['x'], ob['y'], ob['d'], ob['id'])

                start = time.time()
                # Get shortest path
                optimal_path, cost = maze_solver.get_optimal_path()
                runtime = time.time() - start
                total_runtime += runtime
                total_cost += cost
                logger.debug(
                    f"Time taken to find shortest path using A* search: {runtime}s")
                logger.debug(f"cost to travel: {cost} units")

                # Based on the shortest path, generate commands for the robot
                motions, obstacle_id_with_signals, scanned_obstacles = maze_solver.optimal_path_to_motion_path(
                    optimal_path)
                command_generator = CommandGenerator()
                commands = command_generator.generate_commands(
                    motions, obstacle_id_with_signals, scanned_obstacles, optimal_path)
                logger.debug(
                    f"Number of obstacles scanned: {len(scanned_obstacles)} / {len(obstacles)}")

            # Get the starting location and add it to path_results
            path_results = []
            for pos in optimal_path:
                path_results.append(pos.get_dict())

            return marshal(
                {
                    "data": {
                        'distance': total_cost / num_runs,
                        'runtime': total_runtime / num_runs,
                        'path': path_results,
                        'commands': commands,
                        'motions': motions
                    }
                },
                restx_models["SimulatorPathFindingResponse"]
            ), 200
        except Exception as error:
            logger.debug("", exc_info=True)
            return marshal(
                {
                    "error": repr(error)
                },
                restx_models["Error"]
            ), 500


# for API validation to allow only file upload in POST request
file_upload_parser = api.parser()
file_upload_parser.add_argument('file', location='files',
                                type=FileStorage, required=True)


@api.route('/image')
class ImagePredict(Resource):
    @api.expect(file_upload_parser)
    @api.response(model=restx_models["ImagePredictResponse"], code=200, description="Success")
    @api.response(model=restx_models["Error"], code=500, description="Internal Server Error")
    def post(self):
        try:
            """
            For image recognition. Uncomment code for Task 1 / Task 2 respectively
            """
            file = request.files['file']
            filename = file.filename

            # RPI sends image file in format eg. "1739516818_1_C.jpg"
            _, obstacle_id, signal = file.filename.strip(".jpg").split("_")
            logger.debug(
                f"Received image: '{filename}', obstacle_id: {obstacle_id}, signal: {signal}")

            # Store image sent from RPI into uploads folder
            upload_dir = Path("image_rec_files/uploads")
            upload_dir.mkdir(parents=True, exist_ok=True)
            file_path = upload_dir / filename
            file.save(file_path)
            logger.debug(f"Saved raw image into folder: '{upload_dir}'")

            # Call the predict_image function
            # Store processed image with bounding box into output folder
            output_dir = Path("image_rec_files/output/fullsize")
            os.makedirs(output_dir, exist_ok=True)

            # # Week 8 (Task 1)
            # image_id = predict_image(
            #     logger, model, file_path, output_dir, signal)

            # Week 9 (Task 2: only detects arrows & bullseyes)
            image_id = predict_image_t2(
                logger, model, file_path, output_dir, signal)
            return marshal(
                {
                    "obstacle_id": obstacle_id,
                    "image_id": image_id
                },
                restx_models["ImagePredictResponse"]
            )
        except Exception as error:
            logger.debug("", exc_info=True)
            return {
                "error": repr(error)
            }, 500


@api.route('/stitch')
class Stitch(Resource):
    @api.response(model=restx_models["Ok"], code=200, description="Success")
    @api.response(model=restx_models["Error"], code=500, description="Internal Server Error")
    def get(self):
        """
        Concatenates snapped images from RPI, to be shown as proof to examiners
        """
        try:
            output_dir = Path("image_rec_files/output")
            os.makedirs(output_dir, exist_ok=True)

            fullsize_dir = Path("image_rec_files/output/fullsize")
            os.makedirs(fullsize_dir, exist_ok=True)

            img = stitch_image(logger, output_dir, fullsize_dir)
            img.show()
            return marshal(
                {
                    "result": "ok"
                },
                restx_models["Ok"]
            ), 200
        except Exception as error:
            logger.debug(repr(error), exc_info=True)
            return marshal(
                {
                    "error": repr(error)
                },
                restx_models["Error"]
            ), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
