from django.contrib.auth.models import User
from django.contrib.auth import (
    login as django_login,
    logout as django_logout,
    authenticate as django_authenticate
)

from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from accounts.api.serializers import UserSerializer, LoginSerializer

# modelViewSet, to provide user api to read user data
class UserViewSet(viewsets.ModelViewSet): # (ReadOnlyModelViewSet)
    # API endpoint allows users to be viewed or edited
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

class AccountViewSet(viewsets.ViewSet):
    # need to do CRUD ourselves

    @action(methods=['GET'], detail=False) # detail = True if this action is on object
    def login_status(self, request):
        data = {'has_logged_in': request.user.is_authenticated}
        if request.user.is_authenticated:
            data['user'] = UserSerializer(request.user).data
        return Response(data)

    @action(methods=['POST'], detail=False)
    def logout(self, request):
        django_logout(request)
        return Response({'success': True})

    @action(methods=['POST'], detail=False)
    def login(self, request):
        # get username and password from request
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                "success": False,
                "message": "Please check input",
                "errors": serializer.errors,
            }, status=400)