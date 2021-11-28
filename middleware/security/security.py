"""
Google Authentication Class to help with authentication of
the submitted Oauth token.
"""
from flask import g
from middleware.security.google_auth import GoogleAuth

LOGIN_NOT_REQUIRED_PATHS = ["health_check"]


class Security:
    def __init__(self) -> None:
        pass

    @classmethod
    def verify_token(cls, incoming_request):
        """
        The implementation of verification of token; separated from the method
        above for ease in testing.
        """
        if incoming_request.endpoint in LOGIN_NOT_REQUIRED_PATHS:
            return None

        if "Authorization" not in incoming_request.headers:
            return {
                "message": "Request denied access",
                "reason": "Authorization header missing. Please provide an "
                "OAuth2 Token with your request",
            }, 400

        auth_header = incoming_request.headers.get("Authorization")
        if "Bearer " not in auth_header:
            return {
                "message": "Request denied access",
                "reason": "Malformed authorization header provided. Please make sure to "
                "specify the header prefix correctly as 'Bearer ' and try again.",
            }, 400

        # validate the token with Google
        access_token = auth_header.split("Bearer ")[1]
        is_valid, validation = cls.is_valid_token(access_token)
        if not is_valid:
            return {
                "message": "Request denied access",
                "reason": f'Google rejected oauth2 token: {validation["error_description"]}',
            }, 401

        g.access_token = access_token
        g.google_user_id = validation["user_id"]
        return None

    @classmethod
    def is_valid_token(cls, token):
        """
        Takes a token, determines if it is valid and returns the validation resulting
        from the Google Auth API. Determines if the token is valid so that calling function
        does not need to do any additional checks to know the result, but can use the
        error description from the validation provided.
        """
        google_auth = GoogleAuth()
        validation = google_auth.validate_token(token)
        if "error" in validation.keys():
            return False, validation
        return True, validation
