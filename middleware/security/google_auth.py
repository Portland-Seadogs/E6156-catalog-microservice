"""
Google Authentication Class to help with authentication of
the submitted Oauth token.
"""
import requests


class GoogleAuth:
    """
    Authenticates an oauth token with the Google API
    """
    TOKEN_INFO = 'https://www.googleapis.com/oauth2/v1/tokeninfo'
    USER_INFO = "https://www.googleapis.com/oauth2/v2/userinfo"

    def validate_token(self, token):
        """
        Validates a token with the Google Oauth API (which conducts several checks
        on the token to make sure it is still valid, including checking the
        expiration date).
        """
        response = requests.get(self.TOKEN_INFO, params={
                                'access_token': token})
        return response.json()

    def get_user_information(self, token):
        """
        Retrieves all available user information based on the Google Oauth Token
        from the Google Oauth API.
        """
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.get(self.USER_INFO, headers=headers, data={})
        return response.json()
