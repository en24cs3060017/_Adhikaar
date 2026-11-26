"""MongoDB account authentication and optional project feedback storage."""

import base64
import hashlib
import hmac
import os
import secrets
from datetime import datetime, timezone

import streamlit as st


def _setting(name: str, default: str = "") -> str:
    try:
        return str(st.secrets.get(name, os.getenv(name, default))).strip()
    except Exception:
        return os.getenv(name, default).strip()


def _open_database():
    from pymongo import MongoClient

    uri = _setting("MONGODB_URI", "mongodb://localhost:27017")
    client = MongoClient(uri, serverSelectionTimeoutMS=3500)
    try:
        client.admin.command("ping")
    except Exception:
        client.close()
        raise
    return client, client[_setting("MONGODB_DATABASE", "adhikaar_demo")]


def _password_hash(password: str, salt: bytes) -> bytes:
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 310_000, dklen=32)


def create_account(email: str, password: str) -> tuple[bool, str]:
    normalized_email = email.strip().lower()
    salt = secrets.token_bytes(16)
    record = {
        "email": normalized_email,
        "password_salt": base64.b64encode(salt).decode("ascii"),
        "password_hash": base64.b64encode(_password_hash(password, salt)).decode("ascii"),
        "created_at": datetime.now(timezone.utc),
    }
    client = None
    try:
        from pymongo.errors import DuplicateKeyError

        client, database = _open_database()
        users = database["users"]
        users.create_index("email", unique=True)
        users.insert_one(record)
        return True, "Account created. You can now sign in."
    except DuplicateKeyError:
        return False, "An account with this email already exists. Sign in instead."
    except Exception:
        return False, "MongoDB could not be reached. Start the MongoDB service or check MONGODB_URI."
    finally:
        if client is not None:
            client.close()


def verify_account(email: str, password: str) -> tuple[bool, str]:
    normalized_email = email.strip().lower()
    client = None
    try:
        client, database = _open_database()
        record = database["users"].find_one({"email": normalized_email})
        if not record:
            _password_hash(password, b"adhikaar-demo-dummy-salt")
            return False, "Email or password is incorrect."
        salt = base64.b64decode(record["password_salt"])
        expected = base64.b64decode(record["password_hash"])
        actual = _password_hash(password, salt)
        if not hmac.compare_digest(actual, expected):
            return False, "Email or password is incorrect."
        return True, normalized_email
    except Exception:
        return False, "MongoDB could not be reached. Start the MongoDB service or check MONGODB_URI."
    finally:
        if client is not None:
            client.close()


def save_feedback(document: dict) -> tuple[bool, str]:
    client = None
    try:
        client, database = _open_database()
        database["feedback"].insert_one(document)
        return True, "Thanks. Your anonymous project feedback was saved."
    except Exception:
        return False, "Could not reach MongoDB, so this feedback was not saved. Check the connection settings."
    finally:
        if client is not None:
            client.close()
