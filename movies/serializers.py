from rest_framework import serializers
from .models import MovieCollection  # Adjust the import according to your project structure


class MovieCollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MovieCollection
        fields = '__all__'

    def validate(self, attrs):
        # Add any custom validation logic here if necessary
        return attrs
