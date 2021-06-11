import requests
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)

from .provider import CustomProvider


class CustomOAuth2Adapter(OAuth2Adapter):
    provider_id = CustomProvider.id
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


oauth2_login = OAuth2LoginView.adapter_view(CustomOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(CustomOAuth2Adapter)
