import json
import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from django.urls import reverse
from pytest_django.fixtures import client
from rest_framework import status
from rest_framework.test import APIClient

from movies.models import Movie, Book
from .factories import MovieFactory, BookFactory, UserFactory


@pytest.mark.django_db
def test_create_movie(client):
    url = reverse('movies:movie-list')
    data = {"title": "A New Hope",
            "genres": ["Sci-Fi", "Adventure"],
            "release_year": 1997,
            "country": "USA",
            "extra_data": {
                "director": "George Lucas"},
            }

    response = client.post(url, data=data, content_type='application/json')
    assert response.status_code == status.HTTP_201_CREATED, response.json()
    assert Movie.objects.count() == 1


@pytest.mark.django_db
def test_retrieve_movie(client):
    movie = MovieFactory()
    url = reverse('movies:movie-detail', kwargs={'pk': movie.id})

    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data['id'] == movie.id
    assert response.data['title'] == movie.title
    assert response.data['genres'] == movie.genres
    assert response.data['release_year'] == int(movie.release_year)


@pytest.mark.django_db
def test_update_movie(client):
    movie = MovieFactory()
    new_title = "Updated Movie Title"
    url = reverse('movies:movie-detail', kwargs={'pk': movie.id})
    data = {"title": new_title}

    response = client.put(url, data=data, content_type='application/json')
    assert response.status_code == status.HTTP_200_OK, response.json()
    movie = Movie.objects.filter(id=movie.id).first()
    assert movie
    assert movie.title == new_title

@pytest.mark.django_db
def test_delete_movie(client):
    movie = MovieFactory()
    url = reverse('movies:movie-detail', kwargs={'pk': movie.id})
    response = client.delete(url)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not Movie.objects.filter(id=movie.id).exists()

@pytest.mark.django_db
@override_settings(REST_FRAMEWORK={'PAGE_SIZE': 10})
def test_list_movies_with_paginations(client):
    movies = MovieFactory.create_batch(10)
    url = reverse('movies:movie-list')

    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert 'count' in data
    assert 'next' in data
    assert 'previous' in data
    assert 'results' in data

    assert data['count'] == 10
    assert data['next'] is None
    assert data['previous'] is None

    assert len(data['results']) == 10

    returned_movies_ids = {movie['id'] for movie in data['results']}
    expected_movies_ids = {movie.id for movie in movies}
    assert returned_movies_ids == expected_movies_ids

    for movie in data['results']:
        assert set(movie.keys()) == {'id', 'title',
                                     'genres', "release_year",
                                     "country", "extra_data"}


@pytest.mark.django_db
def test_create_book(client):
    url = reverse('movies:book-list')
    data = {
        "title": "The Great Gatsby",
        "author": "F. Scott Fitzgerald",
        "isbn": "0-6631-2012-8",
        "publication_year": 1999,
    }

    response = client.post(url, data=data, content_type='application/json')
    assert response.status_code == status.HTTP_201_CREATED, response.json()
    assert Book.objects.count() == 1


@pytest.mark.django_db
def test_retrieve_book(client):
    book = BookFactory()
    url = reverse('movies:book-detail', kwargs={'pk': book.id})

    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['id'] == book.id
    assert response.data['title'] == book.title
    assert response.data['author'] == book.author
    assert response.data['isbn'] == book.isbn
    assert response.data['publication_year'] == int(book.publication_year)


@pytest.mark.django_db
def test_update_book(client):
    book = BookFactory()
    url = reverse('movies:book-detail', kwargs={'pk': book.id})

    new_title = "Updated Book Title"
    data = {"title": new_title}
    response = client.patch(url, data=data, content_type='application/json')
    assert response.status_code == status.HTTP_200_OK, response.json()
    book = Book.objects.filter(id=book.id).first()
    assert book
    assert book.title == new_title


@pytest.mark.django_db
def test_delete_book(client):
    book = BookFactory()
    url = reverse('movies:book-detail', kwargs={'pk': book.id})
    response = client.delete(url)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not Book.objects.filter(id=book.id).exists()


@pytest.mark.django_db
@override_settings(REST_FRAMEWORK={'PAGE_SIZE': 10})
def test_list_books_with_paginations(client):
    books = BookFactory.create_batch(10)
    url = reverse('movies:book-list')

    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert 'count' in data
    assert 'next' in data
    assert 'previous' in data
    assert 'results' in data

    assert data['count'] == 10
    assert data['next'] is None
    assert data['previous'] is None

    assert len(data['results']) == 10

    returned_books_ids = {book['id'] for book in data['results']}
    expected_book_ids = {book.id for book in books}
    assert returned_books_ids == expected_book_ids

    for book in data['results']:
        assert set(book.keys()) == {'id', 'title', 'author', 'isbn', 'publication_year'}


@pytest.mark.django_db
@pytest.mark.parametrize(
    "new_preferences, expected_genre",
    [
    ({"genre": "sci-fi"}, "sci-fi"),
    ({"genre": "drama"}, "drama"),
    ({"genre": "action"}, "action"),
    ({"genre": "sci-fi", "actor": "Sigourney Weaver", "year": "1979"}, "sci-fi"),
    ]
)
def test_add_and_retrieve_preferences_success(new_preferences, expected_genre):
    user = UserFactory()
    client = APIClient()

    preference_url = reverse("user-preferences", kwargs={"user_id": user.id})

    response = client.post(preference_url, {"new_preferences": new_preferences}, format="json")
    assert response.status_code in [200, 201]

    response = client.get(preference_url)
    assert response.status_code == 200
    assert response.data["genre"] == expected_genre


@pytest.mark.django_db
@pytest.mark.parametrize(
    "new_preferences",
    [
    ({}),
    ({"genreee": "comedy"}),
    ]
)
def test_add_and_retrieve_preferences_failure(new_preferences):
    user = UserFactory()
    client = APIClient()

    preference_url = reverse("user-preferences", kwargs={"user_id": user.id})
    response = client.post(preference_url, {"new_preferences": new_preferences}, format="json")
    assert response.status_code == 400 ,response.json()


@pytest.mark.django_db
def test_add_and_retrieve_watch_history_with_movie_id() -> None:
    user = UserFactory()
    client = APIClient()

    watch_history_url = reverse("user-watch-history", kwargs={"user_id": user.id})
    movie_1 = MovieFactory(title="The Godfather",
                           release_year=1972,
                           directors=["Francis Ford Coppola"],
                           genres= ["Crime", "Drama"])
    movie_2 = MovieFactory(title="Taxi Driver",
                           release_year=1976,
                           directors=["Martin Scorsese"],
                           genres=["Crime", "Drama"])
    for movie in [movie_1, movie_2]:
        response = client.post(watch_history_url, {"movie_id": movie.id}, format="json")
        assert response.status_code == 201, response.json()

    response = client.get(watch_history_url)
    assert response.status_code == 200
    retrieved_movie_ids = [item["title"] for item in response.data["watch_history"]]
    for movie_title in [movie_1.title, movie_2.title]:
        assert movie_title in retrieved_movie_ids

@pytest.mark.django_db
def test_add_invalid_movie_id_to_watch_history() -> None:
    user = UserFactory()
    client = APIClient()

    watch_history_url = reverse("user-watch-history", kwargs={"user_id": user.id})

    invalid_movie_id = 999
    response = client.post(watch_history_url, {"movie_id": invalid_movie_id}, format="json")
    assert response.status_code == 404

test_data = [
    (
        "file.csv",
        "text/csv",
        b"title,genres,extra_data\ntest,comedy,{\"directors\": [\"name\"]}\n",
        201,
    ),
    (
        "file.json",
        "application/json",
        b'[{"title": "test", "genres": ["comedy"], "extra_data": {"directors": ["name"]}}]',
        201,
    ),
    (
        "file.txt",
        "text/plain",
        b"This is a test.",
        400,
    ),
]

@pytest.mark.parametrize(
    "file_name, content_type, file_content, expected_status", test_data
)
@pytest.mark.django_db
def test_general_upload_view(
        client: APIClient,
        file_name: str,
        content_type: str,
        file_content: str,
        expected_status: int):
    url = reverse("movies:file-upload")
    upload_file = SimpleUploadedFile(name=file_name,
                                     content=file_content,
                                     content_type=content_type)
    response = client.post(url, {"file": upload_file}, format="multipart")
    assert response.status_code == expected_status