from rest_framework import serializers
from movies.models import Movie

class MovieSerializer(serializers.Serializer):
    id = serializers.IntegerField(label="Movie ID", required=False)
    title = serializers.CharField(max_length=255)
    genres = serializers.ListSerializer(
        child=serializers.CharField(max_length=100),
        allow_empty=True,
        default=list
    )

    def create(self, validate_data):
        return Movie.objects.create(**validate_data)

    def update(self, instance, validate_data):
        instance.title = validate_data.get('title', instance.title)
        instance.genres = validate_data.get('genres', instance.genres)
        instance.save()
        return instance