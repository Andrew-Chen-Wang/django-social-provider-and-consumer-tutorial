from oauth2_provider.oauth2_validators import OAuth2Validator


class CustomOAuth2Validator(OAuth2Validator):
    def get_additional_claims(self, request):
        """
        JWT Claims are NOT encrypted. They aren't encrypted (I have to repeat
        myself because according to SAT statistics, even with bolded, upper-cased
        letters, many students still miss it.
        """
        # The default for sub is request.user.id, but the clients most likely
        # don't need an ID from your server. That's just my opinion security-wise.
        # In my context, I only need a provider for authentication purposes.
        # However, you might have an endpoint to grab some private content.
        # Then, I'd send sub as the request.user.id to help out your database
        # and send "email": request.user.email as an addition for the client's
        # authentication purposes.
        return {
            "sub": request.user.email,
            "first_name": request.user.first_name,
            "last_name": request.user.last_name,
        }

    def get_userinfo_claims(self, request):
        """
        This just calls self.get_additional_claims, but both are not encrypted!
        This is different in that this is for the /o/userinfo/ endpoint, whereas
        the other is just to get claims during regular authorization flow.

        You can take a look at a sample response here:
        https://openid.net/specs/openid-connect-core-1_0.html#UserInfoResponse

        Example Usage:
        claims = super().get_userinfo_claims(request)
        claims["color_scheme"] = get_color_scheme(request.user)
        return claims
        """
        return super(CustomOAuth2Validator, self).get_userinfo_claims(request)

    def validate_silent_login(self, request):
        pass

    def introspect_token(self, token, token_type_hint, request, *args, **kwargs):
        pass

    def validate_silent_authorization(self, request):
        pass
