from django.contrib.auth.models import User
from django.contrib.auth import (
    login as django_login,
    logout as django_logout,
    authenticate as django_authenticate
)
from accounts.models import UserProfile
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from accounts.api.serializers import (
    LoginSerializer,
    SignupSerializer,
    UserProfileSerializerForUpdate,
    UserSerializer,
)
from utils.permissions import IsObjectOwner
from rest_framework.permissions import IsAuthenticated
from django.utils.decorators import method_decorator
from ratelimit.decorators import ratelimit

# modelViewSet, to provide user api to read user data
class UserViewSet(viewsets.ModelViewSet): # (ReadOnlyModelViewSet)
    # API endpoint allows users to be viewed or edited
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

class AccountViewSet(viewsets.ViewSet):
    # need to do CRUD ourselves
    serializer_class = SignupSerializer

    @action(methods=['GET'], detail=False) # detail = True if this action is on object
    @method_decorator(ratelimit(key='ip', rate='1/s', method='POST', block=True))
    def login_status(self, request):
        data = {'has_logged_in': request.user.is_authenticated}
        if request.user.is_authenticated:
            data['user'] = UserSerializer(request.user).data
        return Response(data)

    @action(methods=['POST'], detail=False)
    @method_decorator(ratelimit(key='ip', rate='1/s', method='POST', block=True))
    def logout(self, request):
        django_logout(request)
        return Response({'success': True})

    @action(methods=['POST'], detail=False)
    @method_decorator(ratelimit(key='ip', rate='1/s', method='POST', block=True))
    def login(self, request):
        # get username and password from request
        # get: request.query_params, post: request.data
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                "success": False,
                "message": "Please check input",
                "errors": serializer.errors,
            }, status=400)
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']

        # check user existence
        if not User.objects.filter(username=username).exists():
            return Response({
                "success": False,
                "message": "User does not exists",
            }, status=400)

        # validate user info
        user = django_authenticate(username=username, password=password)
        if not user or user.is_anonymous:
            return Response({
                "success": False,
                "message": "Username and password do not match",
            }, status=400)

        # login user
        django_login(request, user)
        return Response({
            "success": True,
            "user": UserSerializer(instance=user).data,
        })

    @action(methods=['POST'], detail=False)
    @method_decorator(ratelimit(key='ip', rate='1/s', method='POST', block=True))
    def signup(self, request):
        serializer = SignupSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': "Please check input",
                'errors': serializer.errors,
            }, status=400)

        user = serializer.save()
        # Create UserProfile object
        user.profile
        django_login(request, user)

        return Response({
            'success': True,
            'user': UserSerializer(user).data,
        }, status=201)


class UserProfileViewSet(
    viewsets.GenericViewSet,
    viewsets.mixins.UpdateModelMixin,
):
    queryset = UserProfile
    permission_classes = (IsAuthenticated, IsObjectOwner,)
    serializer_class = UserProfileSerializerForUpdate
