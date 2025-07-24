from contextlib import contextmanager
from typing import Any
from urllib.request import Request

from django.core.files.storage import default_storage
from rest_framework import views, status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework import generics
from rest_framework.views import APIView

from movies.models import Movie, Book
from movies.serializers import (
    MovieSerializer,
    BookSerializer,
    AddPreferenceSerializer,
    AddToWatchHistorySerializer,
    GeneralFileUploadSerializer
)
from movies.services import add_preference, user_preferences, user_watch_history, add_watch_history, FileProcessor
from movies.tasks import process_file

class MovieListCreateAPIView(generics.ListCreateAPIView):
    queryset = Movie.objects.all().order_by("id")
    serializer_class = MovieSerializer

class MovieDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer

class UserPreferencesView(APIView):
    def post(self, request: Request, user_id: int) -> Response | None:
        serializer = AddPreferenceSerializer(data=request.data)
        if serializer.is_valid():
            add_preference(user_id, serializer.validated_data["new_preferences"])
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request: Request, user_id: int) -> Response:
        data = user_preferences(user_id)
        return Response(data)


class WatchHistoryView(APIView):
    def get(self, request: Request, user_id: int) -> Response:
        data = user_watch_history(user_id)
        return Response(data)

    def post(self, request: Request, user_id: int) -> Response:
        serializer = AddToWatchHistorySerializer(data=request.data)
        if serializer.is_valid():
            add_watch_history(
                user_id=user_id,
                movie_id=serializer.validated_data["movie_id"]
            )
            return Response(
                {"message": "Movie added to watch history"},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@contextmanager
def temporary_file(uploaded_file):
    try:
        file_name = default_storage.save(uploaded_file.name, uploaded_file)
        file_path = default_storage.path(file_name)
        yield file_path
    finally:
        default_storage.delete(file_name)

class GeneralUploadView(APIView):
    def post(self, request, *args: Any, **kwargs: Any) -> Response:
        serializer = GeneralFileUploadSerializer(data=request.data)
        if serializer.is_valid():
            upload_file = serializer.validated_data["file"]
            file_type = upload_file.content_type

            with temporary_file(upload_file) as file_path:
                # Celery call using delay
                process_file.delay(file_path, file_type)
                return Response(
                    {"message": "Your file is being processed."},
                    status=status.HTTP_202_ACCEPTED,
                )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BookListCreateAPIView(generics.ListCreateAPIView):
    queryset = Book.objects.all().order_by("id")
    serializer_class = BookSerializer

class BookDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
