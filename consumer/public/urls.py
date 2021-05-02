from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns

from .our_provider import CustomProvider

app_name = "public"
urlpatterns = [] + default_urlpatterns(CustomProvider)
