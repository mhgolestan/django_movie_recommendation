from urllib.request import Request

from rest_framework import views, status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework import generics
from rest_framework.views import APIView

from movies.models import Movie, Book
from movies.serializers import MovieSerializer, BookSerializer, AddPreferenceSerializer, AddToWatchHistorySerializer
from movies.services import add_preference, user_preferences, user_watch_history, add_watch_history


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
        Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
                movie_id=serializer.validated_data["id"]
            )
            return Response(
                {"message": "Movie added to watch history"},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class BookListCreateAPIView(generics.ListCreateAPIView):
    queryset = Book.objects.all().order_by("id")
    serializer_class = BookSerializer

class BookDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
