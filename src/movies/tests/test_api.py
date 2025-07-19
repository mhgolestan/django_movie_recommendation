import json
import pytest
from django.test import override_settings
from django.urls import reverse
from rest_framework import status

from movies.models import Movie
from .factories import MovieFactory

@pytest.mark.django_db
def test_create_movie(client):
    url = reverse('movies:movie-list')
    data = {"title": "A New Hope",
            "genres": ["Sci-Fi", "Adventure"],
            "year": 1997
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
    assert response.data['year'] == int(movie.year)


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
        assert set(movie.keys()) == {'id', 'title', 'genres', "year"}