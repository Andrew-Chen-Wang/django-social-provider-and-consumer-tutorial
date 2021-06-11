"""
Original code from cookiecutter-django
https://github.com/pydanny/cookiecutter-django/blob/master/%7B%7Bcookiecutter.project_slug%7D%7D/%7B%7Bcookiecutter.project_slug%7D%7D/users/adapters.py

This just helps for debugging but also for extensibility
like denying server based registration and only allowing
OAuth + OIDC authorization.
"""
import logging

from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.http import HttpRequest

logger = logging.getLogger(__name__)


class AccountAdapter(DefaultAccountAdapter):
    def is_open_for_signup(self, request: HttpRequest):
        # I only wanted social login only. If you don't really care,
        # I'd still highly recommend using this just for extensibility
        # purposes. Original code from:
        # https://github.com/pydanny/cookiecutter-django/blob/master/%7B%7Bcookiecutter.project_slug%7D%7D/%7B%7Bcookiecutter.project_slug%7D%7D/users/adapters.py
        return False


class SocialAccountAdapter(DefaultSocialAccountAdapter):
    def __init__(self, *args, **kwargs):
        super(SocialAccountAdapter, self).__init__(*args, **kwargs)

    def is_open_for_signup(self, request, sociallogin):
        return True

    # THIS WAS COMPLETELY USELESS (I think. Can't remember)
    # def authentication_error(
    #     self,
    #     request: HttpRequest,
    #     provider_id,
    #     error=None,
    #     exception=None,
    #     extra_context=None,
    # ):
    #     print(f"provider_id {provider_id}")
    #     print(f"error {error}")
    #     print(f"Exception {exception}")
    #     print(f"Extra context {extra_context}")
    #     print("--------------------")
