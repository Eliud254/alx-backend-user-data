#!/usr/bin/env python3
"""
Flask application for user authentication.
"""

from flask import (
    Flask,
    request,
    jsonify,
    abort,
    redirect
)
from auth import Auth

app = Flask(__name__)
AUTH = Auth()


@app.route("/", methods=["GET"], strict_slashes=False)
def index() -> str:
    """
    Return a JSON response with a welcome message.

    Returns:
        str: JSON response with a welcome message.
    """
    return jsonify({"message": "Bienvenue"})


@app.route("/users", methods=["POST"], strict_slashes=False)
def users() -> str:
    """
    Register a new user.

    Args:
        email (str): User's email address.
        password (str): User's password.

    Returns:
        str: JSON response indicating user creation or error message.
    """
    email = request.form.get("email")
    password = request.form.get("password")
    try:
        user = AUTH.register_user(email, password)
    except ValueError:
        return jsonify({"message": "email already registered"}), 400

    return jsonify({"email": email, "message": "user created"})


@app.route("/sessions", methods=["POST"], strict_slashes=False)
def login() -> str:
    """
    Log in a user if the provided credentials are correct and create a new
    session for them.

    Args:
        email (str): User's email address.
        password (str): User's password.

    Returns:
        str: JSON response indicating login status and sets session cookie.
    """
    email = request.form.get("email")
    password = request.form.get("password")

    if not AUTH.valid_login(email, password):
        abort(401)

    session_id = AUTH.create_session(email)
    resp = jsonify({"email": email, "message": "logged in"})
    resp.set_cookie("session_id", session_id)
    return resp


@app.route("/sessions", methods=["DELETE"], strict_slashes=False)
def logout() -> str:
    """
    Log out a logged-in user and destroy their session.

    Returns:
        str: Redirects to the home page.
    """
    session_id = request.cookies.get("session_id")
    user = AUTH.get_user_from_session_id(session_id)
    if user is None or session_id is None:
        abort(403)
    AUTH.destroy_session(user.id)
    return redirect("/")


@app.route("/profile", methods=["GET"], strict_slashes=False)
def profile() -> str:
    """
    Return a user's email based on session_id in the received cookies.

    Returns:
        str: JSON response with the user's email or error message.
    """
    session_id = request.cookies.get("session_id")
    user = AUTH.get_user_from_session_id(session_id)
    if user:
        return jsonify({"email": user.email}), 200
    abort(403)


@app.route("/reset_password", methods=["POST"], strict_slashes=False)
def get_reset_password_token() -> str:
    """
    Generate a token for resetting a user's password.

    Args:
        email (str): User's email address.

    Returns:
        str: JSON response with the reset token or error message.
    """
    email = request.form.get("email")
    try:
        reset_token = AUTH.get_reset_password_token(email)
    except ValueError:
        abort(403)

    return jsonify({"email": email, "reset_token": reset_token})


@app.route("/reset_password", methods=["PUT"], strict_slashes=False)
def update_password() -> str:
    """
    Update a user's password.

    Args:
        email (str): User's email address.
        reset_token (str): Token for resetting the password.
        new_password (str): New password.

    Returns:
        str: JSON response indicating password update status or error message.
    """
    email = request.form.get("email")
    reset_token = request.form.get("reset_token")
    new_password = request.form.get("new_password")

    try:
        AUTH.update_password(reset_token, new_password)
    except ValueError:
        abort(403)

    return jsonify({"email": email, "message": "Password updated"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port="5000")
