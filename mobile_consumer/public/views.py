from datetime import timedelta

import requests
from allauth.socialaccount.models import SocialToken
from django.conf import settings
from django.http import JsonResponse
from django.utils import timezone
from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .provider import CustomProvider


class OAuthTokenSerializer(serializers.Serializer):
    """
    Generic serializer for mobile app to send access and refresh token
    that they got directly from the provider.
    """

    def create(self, validated_data):
        # Not creating any instances here
        pass

    def update(self, instance, validated_data):
        # Not creating any instances here
        pass

    access_token = serializers.CharField(allow_blank=False, trim_whitespace=True)
    refresh_token = serializers.CharField(allow_blank=True, trim_whitespace=True)

    # For our provider, we'd typically force allow_blank=False for both
    # tokens here. For the sake of being general, I've allowed refresh_token token
    # to be blank. The SocialToken model allows refresh token to be a blank str


class TokenObtainPairView(APIView):
    """
    API to return login credentials (an access and refresh token
    pair). This login assumes auto signup is enabled for allauth.

    API view specifically for the custom provider.
    This view uses our setting of automatic signup to immediately
    return a token pair for ourselves to use. If you need more
    info for your signup, for mobile users, you should
    still first get the client to get provider token pair.
    Then, go to this view which says "we don't have an account,
    so you first need to open a web browser (SFSafariViewController)
    inside your app that takes you to this signup continuation page.
    Here's a token to go along with it: CSRF token + UUID to identify
    user temporarily where the UUID is stored in a 10 minute
    expiration cache."
    """

    permission_classes = ()
    authentication_classes = ()

    # localhost domain doesn't matter here since we're using REST API
    # just make sure it matches up with your actual production provider
    access_token_url = "http://127.0.0.1:8001/o/token/"
    authorize_url = "http://127.0.0.1:8001/o/authorize/"
    profile_url = "http://127.0.0.1:8001/o/userinfo/"

    provider = CustomProvider
    expires_in_key = "expires_in"

    def post(self, request):
        serializer = OAuthTokenSerializer(data=request.data)

        non_field_error_key = getattr(
            settings, "NON_FIELD_ERRORS_KEY", "non_field_errors"
        )

        provider = self.provider(request)

        err_r = JsonResponse({non_field_error_key: {"error": "Access token invalid"}})
        if not serializer.is_valid():
            return err_r
        data = serializer.validated_data

        # Create the token
        # from allauth.socialaccount.providers.oauth2.views.OAuth2Adapter.parse_token
        token = SocialToken(token=data["access_token"])
        token.token_secret = data.get("refresh_token", "")
        token.app = provider.get_app(request)
        expires_in = data.get(self.expires_in_key, None)
        if expires_in:
            token.expires_at = timezone.now() + timedelta(seconds=int(expires_in))

        # Verify the access token works
        resp = requests.get(
            self.profile_url,
            params={"access_token": token.token, "alt": "json"},
        )
        if resp.status_code > 299:
            # We've got a problem
            return err_r
        extra_data = resp.json()
        login = provider.sociallogin_from_response(request, extra_data)
        login.lookup()
        if not login.is_existing:
            login.save(request)

        # Create SimpleJWT tokens for consumer authentication purposes
        simple_token = RefreshToken.for_user(login.user)

        def save_info_in_simple_token(_token):
            _token["provider_id"] = provider.id
            _token["provider_access_token"] = data["access_token"]
            _token["provider_refresh_token"] = token.token_secret
            return str(_token)

        return JsonResponse(
            {
                "access_token": save_info_in_simple_token(simple_token.access_token),
                "refresh_token": save_info_in_simple_token(simple_token),
            }
        )
