import pytest

from factories import MovieFactory
from movies.models import Movie

@pytest.mark.django_db
def test_movie_model():
    movie = Movie.objects.create(title="A New Hope", genres=["Sci-Fi", "Adventure"], year=1977)
    assert isinstance(movie, Movie)
    assert movie.title == "A New Hope"
    assert movie.genres == ["Sci-Fi", "Adventure"]
    assert movie.year == 1977