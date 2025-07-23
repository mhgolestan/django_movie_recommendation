import pytest

from movies.models import Movie, Book
from movies.serializers import (
    MovieSerializer,
    BookSerializer,
    PreferencesDetainSerializer,
    AddToWatchHistorySerializer
)


@pytest.mark.django_db
def test_valid_movie_serializer():
    valid_data = {
        "title": "A New Hope",
        "genres": ["Sci-Fi", "Adventure"],
        "release_year": 1997,
        "country": "USA",
        "extra_data": {
            "director": "George Lucas"
        }
    }
    serializer = MovieSerializer(data=valid_data)
    assert serializer.is_valid()
    serializer.save()

    assert Movie.objects.count() == 1
    created_movie = Movie.objects.first()
    assert created_movie.title == valid_data["title"]
    assert created_movie.genres == valid_data["genres"]


@pytest.mark.django_db
def test_invalid_movie_serializer():
    invalid_data = {
        "genres": ["Sci-Fi", "Adventure"]
    }
    serializer = MovieSerializer(data=invalid_data)
    assert not serializer.is_valid()
    assert "title" in serializer.errors


@pytest.mark.django_db
def test_serialize_movie_instance():
    movie = Movie.objects.create(title="A New Hope",
                                 genres=["Sci-Fi", "Adventure"],
                                 release_year=1977)
    serializer = MovieSerializer(movie)
    assert serializer.data == {
        "id": movie.id,
        "title": movie.title,
        "genres": movie.genres,
        "release_year": movie.release_year,
        "country": movie.country,
        "extra_data": movie.extra_data
    }


@pytest.mark.django_db
def test_valid_preferences_serializer():
    valid_data = {
        "genre": "",
        "director": "",
        "actor": "",
        "year": 2010
    }
    serializer = PreferencesDetainSerializer(data=valid_data)
    assert serializer.is_valid()


@pytest.mark.django_db
def test_invalid_preferences_serializer():
    # Test case where all values are empty or None
    all_empty_data = {
        "genre": "",
        "director": "",
        "actor": "",
        "year": None
    }
    serializer = PreferencesDetainSerializer(data=all_empty_data)
    assert not serializer.is_valid()


    invalid_year_data = {
        "year": 1800
    }
    serializer = PreferencesDetainSerializer(data=invalid_year_data)
    assert not serializer.is_valid()
    assert "year" in serializer.errors

    invalid_year_data = {
        "year": 2100
    }
    serializer = PreferencesDetainSerializer(data=invalid_year_data)
    assert not serializer.is_valid()
    assert "year" in serializer.errors


@pytest.mark.django_db
def test_add_to_watch_history_serializer_invalid_data():
    # Test with non-existent movie ID
    invalid_data = {
        "movie_id": 999
    }
    serializer = AddToWatchHistorySerializer(data=invalid_data["movie_id"])
    assert not serializer.is_valid()


@pytest.mark.django_db
def test_add_to_watch_history_serializer_valid_data():
    # Test with valid movie ID
    movie = Movie.objects.create(
        title="Test Movie",
        genres=["Action"],
        release_year=2020
    )
    valid_data = {
        "movie_id": movie.id
    }
    serializer = AddToWatchHistorySerializer(data=valid_data)
    assert serializer.is_valid()


@pytest.mark.django_db
def test_add_to_watch_history_serializer_valid_data_missing_movie_id():
    #Test with missing movie_id
    missing_id_data = {}
    serializer = AddToWatchHistorySerializer(data=missing_id_data)
    assert not serializer.is_valid()
    assert "movie_id" in serializer.errors


@pytest.mark.django_db
def test_add_to_watch_history_serializer_valid_movie_id_type():
    # Test with invalid type for movie_id
    invalid_type_data = {
        "movie_id": "not_an_integer"
    }
    serializer = AddToWatchHistorySerializer(data=invalid_type_data)
    assert not serializer.is_valid()
    assert "movie_id" in serializer.errors


@pytest.mark.django_db
def test_valid_book_serializer():
    valid_data = {
        "title": "The Great Gatsby",
        "author": "F. Scott Fitzgerald",
        "isbn": "0-6631-2012-8",
        "publication_year": 1925
    }
    serializer = BookSerializer(data=valid_data)
    assert serializer.is_valid()
    serializer.save()

    assert Book.objects.count() == 1
    created_book = Book.objects.first()
    assert created_book.title == valid_data["title"]
    assert created_book.author == valid_data["author"]
    assert created_book.isbn == valid_data["isbn"]
    assert created_book.publication_year == valid_data["publication_year"]


@pytest.mark.django_db
def test_invalid_book_serializer():
    invalid_data = {
        "author": "F. Scott Fitzgerald"
    }
    serializer = BookSerializer(data=invalid_data)
    assert not serializer.is_valid()
    assert "title" in serializer.errors


@pytest.mark.django_db
def test_serialize_book_instance():
    book = Book.objects.create(title="The Great Gatsby",
                               author="F. Scott Fitzgerald",
                               isbn="0-6631-2012-8",
                               publication_year=1925)
    serializer = BookSerializer(book)
    assert serializer.data == {
        "id": book.id,
        "title": book.title,
        "author": book.author,
        "isbn": book.isbn,
        "publication_year" : book.publication_year
    }