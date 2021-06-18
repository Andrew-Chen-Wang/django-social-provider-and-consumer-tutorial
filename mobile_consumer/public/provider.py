from allauth.account.models import EmailAddress
from allauth.socialaccount.app_settings import QUERY_EMAIL
from allauth.socialaccount.providers.base import AuthAction, ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider

#
# YOU MUST NAME THIS provider.py OTHERWISE django-allauth won't find the provider
#


class Scope:
    EMAIL = "email"
    PROFILE = "profile"
    OPENID = "openid"


class CustomAccount(ProviderAccount):
    # This is from the google provider. You can obviously
    # replace these methods with the custom claims you
    # added in the provider Django project
    # def get_profile_url(self):
    #     return self.account.extra_data.get("link")
    #
    # def get_avatar_url(self):
    #     return self.account.extra_data.get("picture")

    def to_str(self):
        dflt = super(CustomAccount, self).to_str()
        return self.account.extra_data.get("name", dflt)


class CustomProvider(OAuth2Provider):
    id = "custom"  # Replace with your app/provider name
    name = "Custom"
    account_class = CustomAccount

    def get_default_scope(self):
        # Don't understand why there are these scopes?
        # In the advanced section, I showed you how to add
        # several scopes in the provider section. You can
        # also reference the django-oauth-toolkit docs to
        # better understand that.
        # scope = [Scope.PROFILE]
        # if QUERY_EMAIL:
        #     scope.append(Scope.EMAIL)
        # return scope
        return [Scope.OPENID]

    def get_auth_params(self, request, action):
        ret = super(CustomProvider, self).get_auth_params(request, action)
        if action == AuthAction.REAUTHENTICATE:
            ret["prompt"] = "select_account consent"
        return ret

    def extract_uid(self, data):
        """
        In django-oauth-toolkit, this is the request.user.id. However, I thought
        that was not a good idea since I ONLY needed this for authentication
        purposes only, so instead I implemented email. Visit server/server/oidc.py
        for more information. For MOST use cases, this method should not change.
        Most use cases should also be sending request.user.id not email for sub.
        Visit OpenID docs for more info on what fields could be sent and
        what example values to use.
        """
        return str(data["sub"])

    def extract_common_fields(self, data):
        return dict(
            last_name=data.get("last_name"),
            first_name=data.get("first_name"),
        )

    def extract_email_addresses(self, data):
        ret = [EmailAddress(email=data.get("sub"), verified=True, primary=True)]
        return ret


provider_classes = [CustomProvider]
