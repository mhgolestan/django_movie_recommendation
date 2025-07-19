import datetime

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.conf import settings
from django.db.models import JSONField


class Movie(models.Model):
    title = models.CharField(max_length=255)
    genres = models.JSONField(default=list)
    country = models.CharField(max_length=100, blank=True, null=True)
    extra_data = models.JSONField(default=dict)
    release_year = models.IntegerField(
        validators=[
            MinValueValidator(1888),
            MaxValueValidator(datetime.datetime.now().year)
        ],
        null=True)

    class Meta:
        unique_together = ("title", "country", "release_year")

    def __str__(self):
        return self.title


class UserMoviePreference(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                on_delete=models.CASCADE,
                                related_name="movie_preference")
    preferences = JSONField(default=dict,
                            help_text="Stores user preferences for movies like genres, directors, etc.")
    watch_history = JSONField(default=dict,
                              help_text="Stores information about movies the user has watched.")

    def __str__(self):
        return f"{self.user.username}'s Movie Preferences"



class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    isbn = models.CharField(max_length=13)
    publication_year = models.IntegerField()

    def __str__(self):
        return self.title