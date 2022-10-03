from django.contrib.auth.models import User
from rest_framework import serializers

# encode user object to JSON format
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email')