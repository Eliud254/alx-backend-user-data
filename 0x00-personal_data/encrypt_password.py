#!/usr/bin/env python3
"""Module for password hashing and validation using bcrypt"""
import bcrypt


def hash_password(password: str) -> bytes:
    """
    Generates a bcrypt hash for the given password.

    Args:
        password (str): The password to be hashed.

    Returns:
        bytes: The bcrypt hash of the password.
    """
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())


def is_valid(hashed_password: bytes, password: str) -> bool:
    """
    Verifies a password against a given bcrypt hash.

    Args:
        hashed_password (bytes): The hashed password to verify against.
        password (str): The password to verify.

    Returns:
        bool: True if the password matches the hash, False otherwise.
    """
    return bcrypt.checkpw(password.encode("utf-8"), hashed_password)
