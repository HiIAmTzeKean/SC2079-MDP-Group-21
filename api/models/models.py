from flask_restx import fields


def get_models(api):
    obstacle = api.model('Obstacle', {
        'x': fields.Integer,
        'y': fields.Integer,
        'd': fields.Integer,
        'id': fields.Integer
    })

    path_finding_request = api.model('PathFindingRequest', {
        'obstacles': fields.List(fields.Nested(obstacle)),
        'retrying': fields.Boolean,
        'big_turn': fields.Integer,
        'robot_dir': fields.Integer,
        'robot_x': fields.Integer,
        'robot_y': fields.Integer
    })

    return {
        "Obstacle": obstacle,
        "PathFindingRequest": path_finding_request
    }
