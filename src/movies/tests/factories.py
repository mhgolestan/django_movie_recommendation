from django.contrib.auth import get_user_model
from factory.django import DjangoModelFactory
from factory import Faker
import factory

from movies.models import Movie, Book, UserMoviePreferences


class MovieFactory(DjangoModelFactory):
    class Meta:
        model = Movie

    title = Faker('sentence', nb_words=4)
    genres = Faker('pylist', nb_elements=3,
                   variable_nb_elements=True, value_types=['str'])
    release_year = Faker('year')


class BookFactory(DjangoModelFactory):
    class Meta:
        model = Book

    title = Faker('sentence', nb_words=4)
    author = Faker('name')
    isbn = Faker('isbn13')
    publication_year = Faker('year')


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = get_user_model()

    username = factory.Sequence(lambda n: "user_%d" % n)
    email = factory.LazyAttribute(lambda obj: "%s@example.com" % obj.username)
    password = factory.PostGenerationMethodCall("set_password", "defaultpassword")