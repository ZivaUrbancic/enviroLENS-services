# Logging config script
# Contains the methods for establishing and
# calling the logging function across the service

from flask import jsonify, request

def register(app):
    """Initializes the application for error handling"""

    @app.errorhandler(400)
    def bad_request(e):
        # TODO: possible webpage for error
        return jsonify({
            "error": {
                "message": "400: Bad request",
                "route": request.path,
                "method": request.method,
                "error": e.description,
            }
        })

    @app.errorhandler(401)
    def missing_arguments(e):
        # TODO: possible webpage for error
        return jsonify({
            "error": {
                "message": "401: Bad request. Missing arguments.",
                "route": request.path,
                "method": request.method,
                "error": e.description,
            }
        })

    @app.errorhandler(404)
    def route_not_found(e):
        # TODO: possible webpage for error
        return jsonify({
            "error": {
                "message": "404: Route not found",
                "route": request.path,
                "method": request.method,
                "error": e.description,
            }
        })

    @app.errorhandler(405)
    def method_not_allowed(e):
        # TODO: possible webpage for error
        return jsonify({
            "error": {
                "message": "405: Method not allowed",
                "route": request.path,
                "method": request.method,
                "error": e.description,
            }
        })

    @app.errorhandler(501)
    def method_not_implemented(e):
        # TODO: possible webpage for error
        return jsonify({
            "error": {
                "message": "501: Not implemented",
                "route": request.path,
                "method": request.method,
                "error": e.description,
            }
        })

    @app.errorhandler(502)
    def database_error(e):
        # TODO: possible webpage for error
        return jsonify({
            "error": {
                "message": "502: Database error.",
                "route": request.path,
                "method": request.method,
                "error": e.description,
            }
        })
