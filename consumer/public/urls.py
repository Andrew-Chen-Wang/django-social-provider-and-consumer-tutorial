from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns

from .provider import CustomProvider

app_name = "public"
urlpatterns = [] + default_urlpatterns(CustomProvider)
