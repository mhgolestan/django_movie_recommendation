from django.urls import path
from movies.api import MovieListCreateAPIView, MovieDetailAPIView, BookListCreateAPIView, BookDetailAPIView

app_name = "movies"

urlpatterns = [
    path("movies/", MovieListCreateAPIView.as_view(), name="movie-list"),
    path("movies/<int:pk>/", MovieDetailAPIView.as_view(), name="movie-detail"),
    path("books/", BookListCreateAPIView.as_view(), name="book-list"),
    path("books/<int:pk>/", BookDetailAPIView.as_view(), name="book-detail"),
]