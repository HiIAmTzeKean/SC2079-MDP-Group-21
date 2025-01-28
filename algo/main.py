from algorithms.algo import MazeSolver
from tools.commands import CommandGenerator

from flask import Flask, request, jsonify
from flask_cors import CORS
import time

app = Flask(__name__)
CORS(app)
# model = load_model()
model = None


@app.route('/status', methods=['GET'])
def status():
    """
    This is a health check endpoint to check if the server is running
    :return: a json object with a key "result" and value "ok"
    """
    return jsonify({"result": "ok"})


@app.route('/path', methods=['POST'])
def path_finding():
    """
    This is the main endpoint for the path finding algorithm
    :return: a json object with a key "data" and value a dictionary with keys "distance", "path", and "commands"
    """
    # Get the json data from the request
    content = request.json

    # Get the obstacles, big_turn, retrying, robot_x, robot_y, and robot_direction from the json data
    obstacles = content['obstacles']
    # big_turn = int(content['big_turn'])
    retrying = content['retrying']
    robot_x, robot_y = content['robot_x'], content['robot_y']
    robot_direction = int(content['robot_dir'])

    # Initialize MazeSolver object with robot size of 20x20, bottom left corner of robot at (1,1), facing north, and whether to use a big turn or not.
    # maze_solver = MazeSolver(20, 20, robot_x, robot_y, robot_direction, big_turn=1)
    maze_solver = MazeSolver(size_x=20, size_y=20, robot_x=robot_x, robot_y=robot_y, robot_direction=robot_direction, big_turn=1)
    # Add each obstacle into the MazeSolver. Each obstacle is defined by its x,y positions, its direction, and its id
    for ob in obstacles:
        maze_solver.add_obstacle(ob['x'], ob['y'], ob['d'], ob['id'])

    start = time.time()
    # Get shortest path
    # optimal_path, distance = maze_solver.get_optimal_order_dp(retrying=retrying)
    optimal_path, cost = maze_solver.get_optimal_path(retrying=retrying)
    print(f"Time taken to find shortest path using A* search: {time.time() - start}s")
    print(f"cost to travel: {cost} units")

    # Based on the shortest path, generate commands for the robot
    motions = maze_solver.optimal_path_to_motion_path(optimal_path)
    command_generator = CommandGenerator()
    commands = command_generator.generate_commands(motions, testing=False)

    # Get the starting location and add it to path_results
    path_results = [optimal_path[0].get_dict()]
    for pos in optimal_path:
        path_results.append(pos.get_dict())

    return jsonify({
        "data": {
            'distance': cost,
            'path': path_results,
            'commands': commands
        },
        "error": None
    })


@app.route('/image', methods=['POST'])
def image_predict():
    """
    This is the main endpoint for the image prediction algorithm
    :return: a json object with a key "result" and value a dictionary with keys "obstacle_id" and "image_id"
    """
    file = request.files['file']
    filename = file.filename
    file.save(os.path.join('uploads', filename))
    # filename format: "<timestamp>_<obstacle_id>_<signal>.jpeg"
    constituents = file.filename.split("_")
    obstacle_id = constituents[1]

    ## Week 8 ##
    # signal = constituents[2].strip(".jpg")
    # image_id = predict_image(filename, model, signal)

    ## Week 9 ##
    # We don't need to pass in the signal anymore
    image_id = predict_image_week_9(filename, model)

    # Return the obstacle_id and image_id
    result = {
        "obstacle_id": obstacle_id,
        "image_id": image_id
    }
    return jsonify(result)


@app.route('/stitch', methods=['GET'])
def stitch():
    """
    This is the main endpoint for the stitching command. Stitches the images using two different functions, in effect creating two stitches, just for redundancy purposes
    """
    img = stitch_image()
    img.show()
    img2 = stitch_image_own()
    img2.show()
    return jsonify({"result": "ok"})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)