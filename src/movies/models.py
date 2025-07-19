from django.db import models

class Movie(models.Model):
    title = models.CharField(max_length=255)
    genres = models.JSONField(default=list)
    year = models.IntegerField(null=True)

    def __str__(self):
        return self.title


class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    isbn = models.CharField(max_length=13)
    publication_year = models.IntegerField()

    def __str__(self):
        return self.title