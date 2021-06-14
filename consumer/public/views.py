from urllib.parse import parse_qsl

import requests
from allauth.socialaccount.providers.oauth2.client import (
    OAuth2Client, OAuth2Error,
)
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter, OAuth2CallbackView, OAuth2LoginView,
)
from allauth.utils import get_request_param

from .provider import CustomProvider


class CustomOAuth2Client(OAuth2Client):
    """We need to create a custom class so that we can implement PKCE"""

    def get_access_token(self, code):
        """Mostly copied from allauth, but we need to implement PKCE code_verifier"""
        data = {
            "redirect_uri": self.callback_url,
            "grant_type": "authorization_code",
            "code": code,
            "code_challenge_method": "S256",
            "code_verifier": "",
        }
        if self.basic_auth:  # it's False btw
            auth = requests.auth.HTTPBasicAuth(self.consumer_key, self.consumer_secret)
        else:
            auth = None
            data.update(
                {
                    "client_id": self.consumer_key,
                    "client_secret": self.consumer_secret,
                }
            )
        params = None
        self._strip_empty_keys(data)
        url = self.access_token_url
        if self.access_token_method == "GET":
            params = data
            data = None
        # TODO: Proper exception handling
        resp = requests.request(
            self.access_token_method,
            url,
            params=params,
            data=data,
            headers=self.headers,
            auth=auth,
        )

        access_token = None
        if resp.status_code in [200, 201]:
            # Weibo sends json via 'text/plain;charset=UTF-8'
            if (
                    resp.headers["content-type"].split(";")[0] == "application/json"
                    or resp.text[:2] == '{"'
            ):
                access_token = resp.json()
            else:
                access_token = dict(parse_qsl(resp.text))
        if not access_token or "access_token" not in access_token:
            raise OAuth2Error("Error retrieving access token: %s" % resp.content)
        return access_token


class CustomOAuth2Adapter(OAuth2Adapter):
    provider_id = CustomProvider.id
    client_class = CustomOAuth2Client
    # THESE DOMAINS ARE DIFFERENT FROM CONSUMER DOMAINS. I've been using
    # localhost:8000 for the consumer. For me, I MUST use 127.0.0.1
    # here so that the provider has a different domain and thus a different
    # session cookie between the consumer and provider.
    access_token_url = "http://127.0.0.1:8001/o/token/"
    authorize_url = "http://127.0.0.1:8001/o/authorize/"
    profile_url = "http://127.0.0.1:8001/o/userinfo/"

    def complete_login(self, request, app, token, **kwargs):
        resp = requests.get(
            self.profile_url,
            params={"access_token": token.token, "alt": "json"},
        )
        resp.raise_for_status()
        extra_data = resp.json()
        login = self.get_provider().sociallogin_from_response(request, extra_data)
        return login

    def get_access_token_data(self, request, app, client):
        code = get_request_param(self.request, "code")
        return client.get_access_token(code)


oauth2_login = OAuth2LoginView.adapter_view(CustomOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(CustomOAuth2Adapter)
