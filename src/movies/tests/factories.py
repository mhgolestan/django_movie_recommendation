from factory.django import DjangoModelFactory
from factory import Faker

from movies.models import Movie, Book


class MovieFactory(DjangoModelFactory):
    class Meta:
        model = Movie

    title = Faker('sentence', nb_words=4)
    genres = Faker('pylist', nb_elements=3,
                   variable_nb_elements=True, value_types=['str'])
    year = Faker('year')


class BookFactory(DjangoModelFactory):
    class Meta:
        model = Book

    title = Faker('sentence', nb_words=4)
    author = Faker('name')
    isbn = Faker('isbn13')
    publication_year = Faker('year')

