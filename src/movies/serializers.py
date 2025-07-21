from typing import Any

from rest_framework import serializers
from movies.models import Movie, Book


class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = ["id", "title", "genres", "release_year", "country", "extra_data"]


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ["id", "title", "author", "isbn", "publication_year"]


class PreferencesDetainSerializer(serializers.Serializer):
    genre = serializers.CharField(max_length=100, allow_blank=True, required=False)
    director = serializers.CharField(max_length=100, allow_blank=True, required=False)
    actor = serializers.CharField(max_length=100, allow_blank=True, required=False)
    year = serializers.IntegerField(min_value=1900, max_value=2099, required=False, allow_null=False)

    def validate(self, data: dict[str, Any]) -> dict[str, Any]:
        if all(value in [None, ""] for value in data.values()):
            raise serializers.ValidationError("At least one preference must be provided.")
        return data


class AddPreferenceSerializer(serializers.Serializer):
    new_preferences = PreferencesDetainSerializer()


class AddToWatchHistorySerializer(serializers.Serializer):
    movie_id = serializers.IntegerField()

    def validate_id(self, value: int) -> int:
        if not Movie.objects.filter(id=value).exists():
            raise serializers.ValidationError("Movie with given id does not exist.")
        return value

class PreferencesSerializer(serializers.Serializer):
    genre = serializers.ListField(child=serializers.CharField(),
                                  required=False)
    director = serializers.ListField(child=serializers.CharField(),
                                     required=False)
    actor = serializers.ListField(child=serializers.CharField(),
                                  required=False)
    year = serializers.ListField(child=serializers.CharField(),
                                 required=False)


class WatchHistorySerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255)
    year = serializers.IntegerField()
    director = serializers.CharField(max_length=255)
    genre = serializers.CharField(max_length=255)

