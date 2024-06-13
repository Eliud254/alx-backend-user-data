#!/usr/bin/env python3

import requests

BASE_URL = "http://localhost:5000"


def register_user(email: str, password: str) -> None:
    """
    Register a new user.

    Args:
        email (str): The user's email.
        password (str): The user's password.
    """
    response = requests.post(
        f"{BASE_URL}/users", data={"email": email, "password": password}
    )
    assert response.status_code == 200, f"Registration failed: {response.json()}"
    assert response.json() == {"email": email, "message": "user created"}


def log_in_wrong_password(email: str, password: str) -> None:
    """
    Attempt to log in a user with an incorrect password.

    Args:
        email (str): The user's email.
        password (str): The incorrect password.
    """
    response = requests.post(
        f"{BASE_URL}/sessions", data={"email": email, "password": password}
    )
    assert response.status_code == 401, "Expected 401 Unauthorized"


def log_in(email: str, password: str) -> str:
    """
    Log in a user and return the session ID.

    Args:
        email (str): The user's email.
        password (str): The user's
