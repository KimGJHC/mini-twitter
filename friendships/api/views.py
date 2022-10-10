from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from friendships.models import Friendship
from friendships.api.serializers import (
    FriendshipSerializerForCreate,
    FollowingSerializer,
    FollowerSerializer,
)

from django.contrib.auth.models import User


class FriendshipViewSet(viewsets.GenericViewSet):
    # api example: POST /api/friendships/1/follow is to follower user id = 1
    # detail = True will call get_object() first and check if Friendship object exists
    queryset = User.objects.all()

    @action(methods=['GET'], detail=True, permission_classes=[AllowAny])
    def followers(self, request, pk):
        friendships = Friendship.objects.filter(to_user_id=pk).order_by('-created_at')
        serializer = FollowerSerializer(friendships, many=True)
        return Response(
            {'followers': serializer.data},
            status=status.HTTP_200_OK,
        )

    @action(methods=['GET'], detail=True, permission_classes=[AllowAny])
    def followings(self, request, pk):
        friendships = Friendship.objects.filter(from_user_id = pk).order_by('-created_at')
        serializer = FollowingSerializer(friendships, many=True)

        return Response(
            {'followings': serializer.data},
            status=status.HTTP_200_OK,
        )

    @action(methods=['POST'], detail=True, permission_classes=[IsAuthenticated])
    def follow(self, request, pk):
        # could be the case when follow button is clicked multiple times, do not need to throw exception
        if Friendship.objects.filter(from_user=request.user, to_user=pk).exists():
            return Response({
                'success': True,
                'duplicate': True,
            }, status = status.HTTP_201_CREATED)

        serializer = FriendshipSerializerForCreate(data = {
            'from_user_id': request.user.id,
            'to_user_id': pk,
        })
        if not serializer.is_valid():
            return Response({
                'success': False,
                'errors': serializer.errors,
            }, status = status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response({'success': True},
                        status = status.HTTP_201_CREATED)

    @action(methods=['POST'], detail=True, permission_classes=[IsAuthenticated])
    def unfollow(self, request, pk):
        if request.user.id == int(pk):
            return Response({
                'success': False,
                'message': 'You cannot unfollow yourself',
            }, status = status.HTTP_400_BAD_REQUEST)
        deleted, _ = Friendship.objects.filter(
            from_user=request.user,
            to_user=pk,
        ).delete()
        return Response({'success': True,
                         'deleted': deleted})

    def list(self, request):
        return Response({'message': 'Friendships Home Page'})