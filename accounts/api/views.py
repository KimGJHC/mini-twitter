from django.contrib.auth.models import User
from rest_framework import viewsets, permissions
from accounts.api.serializers import UserSerializer

# modelViewSet, to provide user api to read user data
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]