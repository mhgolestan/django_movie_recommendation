import csv
import json
import sys
from collections import defaultdict
from datetime import datetime
from typing import Any, Tuple

from django.contrib.auth import get_user_model
from django.db import transaction, IntegrityError
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError

from movies.models import UserMoviePreferences, Movie
from movies.serializers import PreferencesSerializer


def add_preference(user_id: int, new_preferences: dict[str,  Any]) -> None:
    with transaction.atomic():
        user = get_object_or_404(get_user_model(), id=user_id)
        (user_preferences, created) = UserMoviePreferences.objects.select_for_update().get_or_create(
            user_id=user_id, defaults={"preferences": {}}
        )
        current_preferences = defaultdict(list, user_preferences.preferences)
        for key, value in new_preferences.items():
            values = value if isinstance(value, list) else [value]
            for val in values:
                if val not in current_preferences[key]:
                    current_preferences[key].append(val)
        user_preferences.preferences = dict(current_preferences)
        user_preferences.save()

def add_watch_history(user_id: int, movie_id: int) -> None:
    user = get_user_model().objects.get(id=user_id)
    movie = get_object_or_404(Movie, id=movie_id)
    movie_info = {
        "title": movie.title,
        "year": movie.release_year,
        "director": movie.extra_data.get("director", []),
        "genres": movie.genres,
    }

    try:
        with transaction.atomic():
            user_preferences, created = UserMoviePreferences.objects.get_or_create(
                user_id=user_id, defaults={"watch_history": [movie_info]}
            )
    except IntegrityError:
        user_preferences = UserMoviePreferences.objects.get(user_id=user_id)
        created = False

    if not created:
        current_watch_history = user_preferences.watch_history
        current_watch_history.append(movie_info)
        user_preferences.watch_history = current_watch_history
        user_preferences.save()


def user_preferences(user_id: int) -> Any:
    user_preferences = get_object_or_404(UserMoviePreferences, user_id=user_id)
    serializer = PreferencesSerializer(user_preferences.preferences)
    return serializer.data

def user_watch_history(user_id: int) -> dict[str, Any]:
    user_preferences = get_object_or_404(UserMoviePreferences, user_id=user_id)
    return {"watch_history": user_preferences.watch_history}

def create_or_update_movie(
    title: str,
    genres: list[str],
    country: str | None = None,
    extra_data: dict[Any, Any] | None = None,
    release_year: int | None = None,
) -> Tuple[Movie, bool]:
    """
    Service function to create or update a Movie instance.
    """
    # Ensure the release_year is within an acceptable range
    current_year = datetime.datetime.now().year
    if release_year is not None and (
        release_year < 1888 or release_year > current_year
    ):
        raise ValidationError(
            "The release year must be between 1888 and the current year."
        )

    # Attempt to update an existing movie or create a new one
    movie, created = Movie.objects.update_or_create(
        title=title,
        defaults={
            "genres": genres,
            "country": country,
            "extra_data": extra_data,
            "release_year": release_year,
        },
    )
    return movie, created


def parse_csv(file_path: str) -> int:
    max_int = sys.maxsize
    while True:
        try:
            csv.field_size_limit(max_int)
            break
        except OverflowError:
            max_int = int(max_int/10)

    movies_processed = 0
    with open(file_path, encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            create_or_update_movie(**row)
            movies_processed += 1
    return movies_processed

def parse_json(file_path: str) -> int:
    movies_processed = 0
    with open(file_path, encoding="utf-8") as file:
        data = json.load(file)
        for item in data:
            create_or_update_movie(**item)
            movies_processed += 1
    return movies_processed

def parse_xml(file_path: str) -> int:
    movies_processed = 0



class FileProcessor:
    def process(self, file_path: str, file_type: str) -> int:
        if file_type == "text/csv":
            movies_processed = parse_csv(file_path)
        elif file_type == "application/json":
            movies_processed = parse_json(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
        return movies_processed

def create_or_update_movie(
        title: str,
        genres: list,
        country: str | None = None,
        extra_data: dict[Any, Any] | None = None,
        release_year: int | None = None
) -> Tuple[Movie, bool]:
    try:
        current_year = datetime.now().year
        if release_year is not None and (release_year < 1888 or release_year > current_year):
            raise ValidationError("The release year must be between 1888 and the current year.")

        movie, created = Movie.objects.update_or_create(
                title=title,
                defaults={
                    "genres": genres,
                    "country": country,
                    "extra_data": extra_data,
                    "release_year": release_year
                }
            )
        return movie, created
    except Exception as e:
        raise ValidationError(f"Failed to create or update the movie: {str(e)}")

