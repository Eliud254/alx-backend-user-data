#!/usr/bin/env python3
"""
Authentication module providing various authentication-related functionalities.
"""

import bcrypt
from uuid import uuid4
from sqlalchemy.orm.exc import NoResultFound
from typing import TypeVar, Union

from db import DB
from user import User

U = TypeVar('U', bound=User)


def _hash_password(password: str) -> bytes:
    """
    Hashes the password string and returns it in bytes form.

    Args:
        password (str): Password in string format.

    Returns:
        bytes: Hashed password in bytes.
    """
    passwd = password.encode('utf-8')
    return bcrypt.hashpw(passwd, bcrypt.gensalt())


def _generate_uuid() -> str:
    """
    Generates a UUID and returns its string representation.

    Returns:
        str: String representation of a UUID.
    """
    return str(uuid4())


class Auth:
    """
    Auth class to interact with the authentication database.
    """

    def __init__(self) -> None:
        """
        Initialize a new Auth instance with a database connection.
        """
        self._db = DB()

    def register_user(self, email: str, password: str) -> User:
        """
        Register a new user and return a User object.

        Args:
            email (str): New user's email address.
            password (str): New user's password.

        Returns:
            User: Newly created User object.

        Raises:
            ValueError: If a user with the given email already exists.
        """
        try:
            self._db.find_user_by(email=email)
        except NoResultFound:
            hashed = _hash_password(password)
            usr = self._db.add_user(email, hashed)
            return usr
        raise ValueError(f"User {email} already exists")

    def valid_login(self, email: str, password: str) -> bool:
        """
        Validate a user's login credentials.

        Args:
            email (str): User's email address.
            password (str): User's password.

        Returns:
            bool: True if credentials are correct, else False.
        """
        try:
            user = self._db.find_user_by(email=email)
        except NoResultFound:
            return False

        user_password = user.hashed_password
        passwd = password.encode("utf-8")
        return bcrypt.checkpw(passwd, user_password)

    def create_session(self, email: str) -> Union[None, str]:
        """
         session_id for an existing user. update their session_id attribute

        Args:
            email (str): User's email address.

        Returns:
            Union[None, str]:create session_id or None if user not found
        """
        try:
            user = self._db.find_user_by(email=email)
        except NoResultFound:
            return None

        session_id = _generate_uuid()
        self._db.update_user(user.id, session_id=session_id)
        return session_id

    def get_user_from_session_id(self, session_id: str) -> Union[None, U]:
        """
        Get a user from their session_id.

        Args:
            session_id (str): Session ID of the user.

        Returns:
            Union[None, U]: User object if found, else None.
        """
        if session_id is None:
            return None

        try:
            user = self._db.find_user_by(session_id=session_id)
        except NoResultFound:
            return None

        return user

    def destroy_session(self, user_id: int) -> None:
        """
        Destroy a user's session by setting their session_id attribute to None.

        Args:
            user_id (int): User's ID.

        Returns:
            None
        """
        try:
            self._db.update_user(user_id, session_id=None)
        except ValueError:
            return None
        return None

    def get_reset_password_token(self, email: str) -> str:
        """
        Generate a reset_token UUID for a user identified by their email.

        Args:
            email (str): User's email address.

        Returns:
            str: Newly generated reset_token for the user.

        Raises:
            ValueError: If no user is found with the given email.
        """
        try:
            user = self._db.find_user_by(email=email)
        except NoResultFound:
            raise ValueError

        reset_token = _generate_uuid()
        self._db.update_user(user.id, reset_token=reset_token)
        return reset_token

    def update_password(self, reset_token: str, password: str) -> None:
        """
        Update a user's password.

        Args:
            reset_token (str): Reset token issued for password reset.
            password (str): New password for the user.

        Returns:
            None

        Raises:
            ValueError: If no user is found with the given reset_token.
        """
        try:
            user = self._db.find_user_by(reset_token=reset_token)
        except NoResultFound:
            raise ValueError

        hashed = _hash_password(password)
        self._db.update_user(user.id, hashed_password=hashed, reset_token=None)
