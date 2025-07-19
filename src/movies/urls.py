from django.urls import path
from movies.api import MovieAPIView

app_name = "movies"

urlpatterns = [
    path("movies/", MovieAPIView.as_view(), name="movie-list"),
    path("movies/<int:pk>/", MovieAPIView.as_view(), name="movie-detail"),
]