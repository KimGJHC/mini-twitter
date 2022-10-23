# serializer converts objects into data type that is understandable by front end
from accounts.api.serializers import UserSerializerForFriendship
from friendships.models import Friendship
from friendships.services import FriendshipService
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

class FriendshipSerializerForCreate(serializers.ModelSerializer):
    from_user_id = serializers.IntegerField()
    to_user_id = serializers.IntegerField()

    class Meta:
        model = Friendship
        fields = ('from_user_id', 'to_user_id')

    def validate(self, attrs): # attrs is a dictionary
        if attrs['from_user_id'] == attrs['to_user_id']:
            raise  ValidationError({
                'message': 'from_user_id and to_user_id should be different'
            })
        return attrs

    def create(self, validated_data):
        from_user_id = validated_data['from_user_id']
        to_user_id = validated_data['to_user_id']

        return Friendship.objects.create(
            from_user_id = from_user_id,
            to_user_id = to_user_id,
        )


# use source to visited model instance's methods
class FollowerSerializer(serializers.ModelSerializer):
    user = UserSerializerForFriendship(source='from_user')
    created_at = serializers.DateTimeField()
    has_followed = serializers.SerializerMethodField()

    class Meta:
        model = Friendship
        fields = ('user', 'created_at', 'has_followed')

    def get_has_followed(self, obj):
        if self.context['request'].user.is_anonymous:
            return False
        # this implementation has n+1 query problem
        return FriendshipService.has_followed(self.context['request'].user, obj.from_user)

class FollowingSerializer(serializers.ModelSerializer):
    user = UserSerializerForFriendship(source='to_user')
    created_at = serializers.DateTimeField()
    has_followed = serializers.SerializerMethodField()

    class Meta:
        model = Friendship
        fields = ('user', 'created_at', 'has_followed')

    def get_has_followed(self, obj):
        if self.context['request'].user.is_anonymous:
            return False
        return FriendshipService.has_followed(self.context['request'].user, obj.to_user)
