#!/usr/bin/env python3
"""Main module for the user authentication service."""
import requests


EMAIL = "guillaume@holberton.io"
PASSWD = "b4l0u"
NEW_PASSWD = "t4rt1fl3tt3"
BASE_URL = "http://0.0.0.0:5000"


def register_user(email: str, password: str) -> None:
    """Tests registering a new user.
    """
    url = "{}/users".format(BASE_URL)
    body = {
        'email': email,
        'password': password,
    }
    response = requests.post(url, data=body)
    assert response.status_code == 200
    assert response.json() == {"email": email, "message": "user created"}
    response = requests.post(url, data=body)
    assert response.status_code == 400
    assert response.json() == {"message": "email already registered"}


def log_in_wrong_password(email: str, password: str) -> None:
    """Tests logging in with a wrong password.
    """
    login_url = "{}/sessions".format(BASE_URL)
    login_payload = {
        'email': email,
        'password': password,
    }
    login_response = requests.post(login_url, data=login_payload)
    assert login_response.status_code == 401


def log_in(email: str, password: str) -> str:
    """Tests logging in with the correct password.
    """
    login_url = "{}/sessions".format(BASE_URL)
    login_data = {
        'email': email,
        'password': password,
    }
    response = requests.post(login_url, data=login_data)
    assert response.status_code == 200
    assert response.json() == {"email": email, "message": "logged in"}
    return response.cookies.get('session_id')


def profile_unlogged() -> None:
    """Tests retrieving profile information whilst not logged in.
    """
    profile_url = "{}/profile".format(BASE_URL)
    profile_response = requests.get(profile_url)
    assert profile_response.status_code == 403


def profile_logged(session_id: str) -> None:
    """Tests retrieving profile information whilst logged in.
    """
    profileUrl = "{}/profile".format(BASE_URL)
    session_cookies = {
        'session_id': session_id,
    }
    profile_response = requests.get(profileUrl, cookies=session_cookies)
    assert profile_response.status_code == 200
    assert "email" in profile_response.json()


def log_out(session_id: str) -> None:
    """Tests logging out.
    """
    logout_url = "{}/sessions".format(BASE_URL)
    requestCookies = {
        'session_id': session_id,
    }
    response = requests.delete(logout_url, cookies=requestCookies)
    assert response.status_code == 200
    assert response.json() == {"message": "Bienvenue"}


def reset_password_token(email: str) -> str:
    """Tests requesting a password reset.
    """
    resetUrl = "{}/reset_password".format(BASE_URL)
    reset_data = {'email': email}
    response = requests.post(resetUrl, data=reset_data)
    assert response.status_code == 200
    assert "email" in response.json()
    assert response.json()["email"] == email
    assert "reset_token" in response.json()
    return response.json().get('reset_token')


def update_password(email: str, reset_token: str, new_password: str) -> None:
    """Tests updating a password.
    """
    resetPasswordUrl = "{}/reset_password".format(BASE_URL)
    password_update_request = {
        'email': email,
        'reset_token': reset_token,
        'new_password': new_password,
    }
    response = requests.put(
        resetPasswordUrl,
        data=password_update_request)
    assert response.status_code == 200
    assert response.json() == {"email": email, "message": "Password updated"}


if __name__ == "__main__":
    register_user(EMAIL, PASSWD)
    log_in_wrong_password(EMAIL, NEW_PASSWD)
    profile_unlogged()
    session_id = log_in(EMAIL, PASSWD)
    profile_logged(session_id)
    log_out(session_id)
    reset_token = reset_password_token(EMAIL)
    update_password(EMAIL, reset_token, NEW_PASSWD)
    log_in(EMAIL, NEW_PASSWD)
