import pytest

from movies.models import Movie, Book
from movies.serializers import MovieSerializer, BookSerializer

@pytest.mark.django_db
def test_valid_movie_serializer():
    valid_data = {
        "title": "A New Hope",
        "genres": ["Sci-Fi", "Adventure"],
        "year": 1997
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
    movie = Movie.objects.create(title="A New Hope", genres=["Sci-Fi", "Adventure"], year=1977)
    serializer = MovieSerializer(movie)
    assert serializer.data == {
        "id": movie.id,
        "title": movie.title,
        "genres": movie.genres,
        "year": movie.year
    }


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