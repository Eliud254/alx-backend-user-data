#!/usr/bin/env python3
"""
Flask application for user authentication and password management.
"""
from flask import Flask, jsonify, request, abort, redirect
from auth import Auth

app = Flask(__name__)
AUTH = Auth()


@app.route("/", methods=["GET"])
def welcome() -> str:
    """
    Endpoint: GET /
    Returns a JSON response with a welcome message.
    """
    return jsonify({"message": "Bienvenue"})


@app.route("/users", methods=["POST"])
def create_user() -> str:
    """
    Endpoint: POST /users
    Register a new user.
    Returns:
        JSON: User's email and a success message if user is
        created successfully,therwise returns an error message
        if the email is already registered.
    """
    email = request.form["email"]
    password = request.form["password"]
    try:
        user = AUTH.register_user(email, password)
        return jsonify({"email": email, "message": "user created"}), 200
    except ValueError:
        return jsonify({"message": "email already registered"}), 400


@app.route("/sessions", methods=["POST"])
def login() -> str:
    """
    Endpoint: POST /sessions
    Log in a user.
    Returns:
        JSON: User's email and a success message if login is successful,
              otherwise aborts with a 401 status code
              if credentials are invalid.
    """
    email = request.form.get("email")
    password = request.form.get("password")

    if AUTH.valid_login(email, password):
        response = jsonify({"email": email, "message": "logged in"}), 200
        response.set_cookie("session_id", AUTH.create_session(email))
        return response
    else:
        abort(401)


@app.route("/sessions", methods=["DELETE"])
def logout() -> str:
    """
    Endpoint: DELETE /sessions
    Log out a user by deleting their session.
    Returns:
        Redirect: Redirects to '/' if session is successfully destroyed,
                  otherwise aborts with a 403 status code if session
                  ID is invalid.
    """
    session_id = request.cookies.get("session_id")
    user = AUTH.get_user_from_session_id(session_id)
    if user is None:
        abort(403)
    AUTH.destroy_session(user.id)
    return redirect("/")


@app.route("/profile", methods=["GET"])
def get_profile() -> str:
    """
    Endpoint: GET /profile
    Retrieve user's profile based on session ID.
    Returns:
        JSON: User's email if session is valid, otherwise aborts with
        403 status code if session ID is invalid.
    """
    session_id = request.cookies.get("session_id")
    user = AUTH.get_user_from_session_id(session_id)
    if user:
        return jsonify({"email": user.email}), 200
    else:
        abort(403)


@app.route("/reset_password", methods=["POST"])
def get_reset_password_token() -> str:
    """
    Endpoint: POST /reset_password
    Generate a password reset token for a user.
    Returns:
        JSON: User's email and reset token if user is found,
              otherwise aborts with 403 status code if user is not found.
    """
    email = request.form.get("email")

    try:
        reset_token = AUTH.get_reset_password_token(email)
        return jsonify({"email": email, "reset_token": reset_token}), 200
    except ValueError:
        abort(403)


@app.route("/reset_password", methods=["PUT"])
def update_password() -> str:
    """
    Endpoint: PUT /reset_password
    Update user's password using a reset token.
    Returns:
        JSON: User's email and a success message if password is updated
              successfully,otherwise aborts with 403 status code
              if reset token is invalid.
    """
    email = request.form.get("email")
    reset_token = request.form.get("reset_token")
    new_password = request.form.get("new_password")
    try:
        AUTH.update_password(reset_token, new_password)
        return jsonify({"email": email, "message": "Password updated"}), 200
    except ValueError:
        abort(403)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port="5000")
