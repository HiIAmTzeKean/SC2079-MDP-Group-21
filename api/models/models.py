from flask_restx import fields


def get_models(api):
    obstacle = api.model('Obstacle', {
        'x': fields.Integer(required=True, min=0, max=19, default=10),
        'y': fields.Integer(required=True, min=0, max=19, default=10),
        'd': fields.Integer(required=True, min=0, max=8, multiple=2, default=4),
        'id': fields.Integer(required=True)
    })

    position = api.model('Position', {
        'x': fields.Integer(),
        'y': fields.Integer(),
        'd': fields.Integer(),
        's': fields.String()
    })

    path_finding_request = api.model('PathFindingRequest', {
        'obstacles': fields.List(fields.Nested(obstacle), required=True),
        'retrying': fields.Boolean(required=False, default=False),
        'robot_dir': fields.Integer(required=False, min=0, max=6, multiple=2, default=0),
        'robot_x': fields.Integer(required=False, min=0, max=19, default=1),
        'robot_y': fields.Integer(required=False, min=0, max=19, default=1),
    })

    path_finding_data = api.model('PathFindingData', {
        'commands': fields.List(fields.String()),
        'path': fields.List(fields.Nested(position)),
    })

    path_finding_response = api.model('PathFindingResponse', {
        'data': fields.Nested(path_finding_data),
    })

    simulator_path_finding_request = api.model('SimulatorPathFindingRequest', {
        'obstacles': fields.List(fields.Nested(obstacle), required=True),
        'retrying': fields.Boolean(required=False, default=False),
        'robot_dir': fields.Integer(required=False, min=0, max=6, multiple=2, default=0),
        'robot_x': fields.Integer(required=False, min=0, max=19, default=1),
        'robot_y': fields.Integer(required=False, min=0, max=19, default=1),
        'num_runs': fields.Integer(required=False, min=1)
    })

    simulator_path_finding_data = api.model('SimulatorPathFindingData', {
        'commands': fields.List(fields.String()),
        'distance': fields.Float(),
        'path': fields.List(fields.Nested(position)),
        'runtime': fields.Float(),
        'motions': fields.List(fields.String()),
    })

    simulator_path_finding_response = api.model('SimulatorPathFindingResponse', {
        'data': fields.Nested(simulator_path_finding_data),
    })

    image_predict_response = api.model('ImagePredictResponse', {
        "obstacle_id": fields.String(),
        "image_id": fields.String(),
    })

    error = api.model('Error', {
        'error': fields.String()
    })

    ok = api.model('Ok', {
        'result': fields.String()
    })

    return {
        "Obstacle": obstacle,
        "PathFindingRequest": path_finding_request,
        "PathFindingResponse": path_finding_response,
        "SimulatorPathFindingRequest": simulator_path_finding_request,
        "SimulatorPathFindingResponse": simulator_path_finding_response,
        "ImagePredictResponse": image_predict_response,
        "Error": error,
        "Ok": ok,
    }
