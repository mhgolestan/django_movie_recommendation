import json
import pytest
from django.test import override_settings
from django.urls import reverse
from rest_framework import status

from movies.models import Movie, Book
from .factories import MovieFactory, BookFactory


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
