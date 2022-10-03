from django.contrib.auth.models import User
from rest_framework import serializers

# 1. encode user object to JSON format for frontend
# 2. validate user data
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email')



class LoginSerializer(serializers.Serializer):
    # check if username or password is empty
    username = serializers.CharField()
    password = serializers.CharField()