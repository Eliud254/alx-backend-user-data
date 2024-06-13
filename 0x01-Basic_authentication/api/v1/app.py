#!/usr/bin/env python3
"""
API Route Handler

"""

from os import getenv
from typing import Dict, Tuple
from api.v1.views import app_views
from flask import Flask, jsonify, abort, request
from flask_cors import CORS, cross_origin

# Configure CORS (Cross-Origin Resource Sharing)
app = Flask(__name__)
app.register_blueprint(app_views)
CORS(app, resources={r"/api/v1/*": {"origins": "*"}})

# Initialize authentication handler based on environment variable
auth = None
auth_type = getenv("AUTH_TYPE")
if auth_type == "basic_auth":
  auth = BasicAuth()
elif auth_type == "auth":
  auth = Auth()
else:
  print(f"WARNING: Unknown AUTH_TYPE: {auth_type}. Authentication disabled.")

# Authentication check before each request
@app.before_request
def before_request_func():
  """
  This function intercepts requests before processing. 
  - If no authentication is configured, it does nothing.
  - If authentication is required for the requested path and not provided, 
    it returns a 401 (Unauthorized) error.
  - If authentication headers are missing, it returns a 401 error.
  - If user authentication fails, it returns a 403 (Forbidden) error.
  """
  if auth is None:
    return
  if not auth.require_auth(request.path, exempt_paths=[
      '/api/v1/status/',
      '/api/v1/unauthorized/',
      '/api/v1/forbidden/'
  ]):
    return  # No authentication required for these paths
  if auth.authorization_header(request) is None:
    abort(401)  # Missing Authorization header
  if auth.current_user(request) is None:
    abort(403)  # Invalid user authentication

# Error handlers for common HTTP status codes

@app.errorhandler(401)
def unauthorized(error):
  """
  Handles 401 (Unauthorized) errors by returning a JSON response 
  with an error message.
  """
  return jsonify({"error": "Unauthorized"}), 401

@app.errorhandler(403)
def forbidden(error):
  """
  Handles 403 (Forbidden) errors by returning a JSON response 
  with an error message.
  """
  return jsonify({"error": "Forbidden"}), 403

@app.errorhandler(404)
def not_found(error):
  """
  Handles 404 (Not Found) errors by returning a JSON response 
  with an error message.
  """
  return jsonify({"error": "Not found"}), 404

# Run the Flask application

if __name__ == "__main__":
  host = getenv("API_HOST", "0.0.0.0")
  port = getenv("API_PORT", "5000")
  app.run(host=host, port=port)
