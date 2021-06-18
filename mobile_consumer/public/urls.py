from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import TokenObtainPairView

app_name = "public"
urlpatterns = [
    # Gets both access and refresh tokens
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    # Send refresh token; receive new short-lived access token
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
