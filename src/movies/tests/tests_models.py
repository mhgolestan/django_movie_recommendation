import pytest

from movies.models import Movie, Book

@pytest.mark.django_db
def test_movie_model():
    movie = Movie.objects.create(title="A New Hope", genres=["Sci-Fi", "Adventure"], year=1977)
    assert isinstance(movie, Movie)
    assert movie.title == "A New Hope"
    assert movie.genres == ["Sci-Fi", "Adventure"]
    assert movie.year == 1977

@pytest.mark.django_db
def test_book_model():
    book = Book.objects.create(title="The Great Gatsby",
                               author="F. Scott Fitzgerald",
                               isbn="0-6631-2012-8",
                               publication_year=1925)
    assert isinstance(book, Book)
    assert book.title == "The Great Gatsby"
    assert book.author == "F. Scott Fitzgerald"
    assert book.isbn == "0-6631-2012-8"
    assert book.publication_year == 1925