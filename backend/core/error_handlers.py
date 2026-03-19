"""
Global error handlers for API and frontend routes.

Provides JSON error responses for API routes and SPA fallback for frontend routes.
"""

from pathlib import Path
from flask import request, jsonify, render_template, send_from_directory
from backend.core.config import BASE_DIR

FRONTEND_DIST_DIR = BASE_DIR / 'frontend' / 'dist'
API_ROUTE_PREFIXES = ('/api/', '/canvas/', '/hql-preview-v2/')


def _is_api_request():
    """Check if the current request is targeting an API endpoint."""
    return request.path.startswith(API_ROUTE_PREFIXES)


def register_error_handlers(app):
    """Register global error handlers on the Flask app."""

    @app.errorhandler(400)
    def bad_request_error(error):
        if _is_api_request():
            return jsonify({
                'success': False,
                'error': 'Bad Request',
                'message': str(error),
                'timestamp': None
            }), 400
        return error

    @app.errorhandler(404)
    def not_found_error(error):
        if _is_api_request():
            from datetime import datetime
            return jsonify({
                'success': False,
                'error': 'Resource not found',
                'message': 'The requested resource was not found',
                'timestamp': datetime.now().isoformat()
            }), 404
        try:
            return send_from_directory(str(FRONTEND_DIST_DIR), 'index.html')
        except FileNotFoundError:
            return render_template('errors/404.html'), 404

    @app.errorhandler(405)
    def method_not_allowed_error(error):
        if _is_api_request():
            return jsonify({
                'success': False,
                'error': 'Method Not Allowed',
                'message': 'The method is not allowed for the requested URL',
                'timestamp': None
            }), 405
        return error

    @app.errorhandler(500)
    def internal_server_error(error):
        if _is_api_request():
            return jsonify({
                'success': False,
                'error': 'Internal Server Error',
                'message': 'An unexpected error occurred',
                'timestamp': None
            }), 500
        return error
