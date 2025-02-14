
from werkzeug.datastructures import FileStorage
import time
from flask_restx import Resource, Api
from flask_cors import CORS
from flask import Flask, request, jsonify
from pathlib import Path
from models.models import get_models

import sys
import os
# Allows Python to find package from sibling directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from algo.algorithms.algo import MazeSolver  # nopep8
from algo.tools.commands import CommandGenerator  # nopep8
from image_rec.model import load_model, predict_image, stitch_image  # nopep8

app = Flask(__name__)

api = Api(app, validate=True)
restx_models = get_models(api)

CORS(app)

# load model for image recognition
model = load_model()


@api.route('/status')
class Status(Resource):
    def get(self):
        """
        This is a health check endpoint to check if the server is running
        :return: a json object with a key "result" and value "ok"
        """
        return jsonify({"result": "ok"})


@api.route('/path')
class PathFinding(Resource):
    @api.expect(restx_models["PathFindingRequest"])
    @api.marshal_with(restx_models["PathFindingResponse"])
    def post(self):
        """
        This is the main endpoint for the path finding algorithm
        :return: a json object with a key "data" and value a dictionary with keys "distance", "path", and "commands"
        """
        # Get the json data from the request
        content = request.json

        # Get the obstacles, retrying, robot_x, robot_y, and robot_direction from the json data
        obstacles = content['obstacles']
        # TODO: use alternative algo for retrying?
        retrying = content.get('retrying', False)
        robot_x, robot_y = content.get('robot_x', 1), content.get('robot_y', 1)
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
        print(
            f"Time taken to find shortest path using A* search: {runtime}s")
        print(f"cost to travel: {cost} units")

        # Based on the shortest path, generate commands for the robot
        motions, obstacle_ids = maze_solver.optimal_path_to_motion_path(
            optimal_path)
        command_generator = CommandGenerator()
        commands = command_generator.generate_commands(
            motions, obstacle_ids)

        # Get the starting location and add it to path_results
        path_results = []
        for pos in optimal_path:
            path_results.append(pos.get_dict())

        return {
            "data": {
                'path': path_results,
                'commands': commands,
            },
            "error": None
        }


# FOR SIMULATOR TESTING ONLY
@api.route('/simulator_path')
class SimulatorPathFinding(Resource):
    @api.expect(restx_models["SimulatorPathFindingRequest"])
    @api.marshal_with(restx_models["SimulatorPathFindingResponse"])
    def post(self):
        """
        FOR SIMULATOR TESTING ONLY. RPI SHOULD NOT BE USING THIS ENDPOINT
        :return: a json object with a key "data" and value a dictionary with keys "distance", "path", and "commands"
        """
        # Get the json data from the request
        content = request.json

        # Get the obstacles, retrying, robot_x, robot_y, and robot_direction from the json data
        obstacles = content['obstacles']
        # TODO: use alternative algo for retrying?
        retrying = content.get('retrying', False)
        robot_x, robot_y = content.get('robot_x', 1), content.get('robot_y', 1)
        robot_direction = content.get('robot_dir', 0)
        num_runs = content.get('num_runs', 1)  # for testing

        optimal_path, commands, total_cost, total_runtime, = None, None, 0, 0
        for _ in range(num_runs):
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
            total_runtime += runtime
            total_cost += cost
            print(
                f"Time taken to find shortest path using A* search: {runtime}s")
            print(f"cost to travel: {cost} units")

            # Based on the shortest path, generate commands for the robot
            motions, obstacle_ids = maze_solver.optimal_path_to_motion_path(
                optimal_path)
            command_generator = CommandGenerator()
            commands = command_generator.generate_commands(
                motions, obstacle_ids)

        # Get the starting location and add it to path_results
        path_results = []
        for pos in optimal_path:
            path_results.append(pos.get_dict())

        return {
            "data": {
                'distance': total_cost / num_runs,
                'runtime': total_runtime / num_runs,
                'path': path_results,
                'commands': commands,
                'motions': motions
            },
            "error": None
        }


# for API validation to allow only file upload in POST request
file_upload_parser = api.parser()
file_upload_parser.add_argument('file', location='files',
                                type=FileStorage, required=True)


@api.route('/image')
class ImagePredict(Resource):
    @api.expect(file_upload_parser)
    @api.marshal_with(restx_models["ImagePredictResponse"])
    def post(self):
        """
        This is the main endpoint for the image prediction algorithm
        :return: a json object of a dictionary with keys "obstacle_id" and "image_id"
        """
        file = request.files['file']
        filename = file.filename

        # RPI sends image file in format eg. "1739516818_1_C.jpg"
        _, obstacle_id, signal = file.filename.strip(".jpg").split("_")

        # Store image sent from RPI into uploads folder
        upload_dir = Path("image_rec_files/uploads")
        upload_dir.mkdir(exist_ok=True)
        file_path = upload_dir / filename
        file.save(file_path)

        # Call the predict_image function
        # Store processed image with bounding box into output folder
        output_dir = Path("image_rec_files/output")
        os.makedirs(output_dir, exist_ok=True)

        image_id = predict_image(model, file_path, output_dir)

        return {
            "obstacle_id": obstacle_id,
            "image_id": image_id
        }


@api.route('/stitch')
class Stitch(Resource):
    def get(self):
        """
        This is the main endpoint for the stitching command. Stitches the images using two different functions, in effect creating two stitches, just for redundancy purposes
        """
        img = stitch_image()
        img.show()
        return jsonify({"result": "ok"})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
