# service is interacting with data model
from django.core.cache import caches
from django.conf import settings
from friendships.models import Friendship
from twitter.cache import FOLLOWINGS_PATTERN

cache = caches['testing'] if settings.TESTING else caches['default']

class FriendshipService(object):

    @classmethod
    def get_followers(cls, user):
        # 1. avoid n+1 queries problem
        # 2. avoid join operation (.select_related())
        # use in operation (.prefetch_related)

        friendships = Friendship.objects.filter(
            to_user=user,
        ).prefetch_related('from_user')
        return [friendship.from_user for friendship in friendships]

    @classmethod
    def get_follower_ids(cls, to_user_id):
        friendships = Friendship.objects.filter(to_user_id=to_user_id)
        return [friendship.from_user_id for friendship in friendships]

    @classmethod
    def get_following_user_id_set(cls, from_user_id):
        key = FOLLOWINGS_PATTERN.format(user_id=from_user_id)
        # check if key is in cache
        user_id_set = cache.get(key)
        if user_id_set is not None:
            return user_id_set
        # retrieve from db if key is not in cache
        friendships = Friendship.objects.filter(from_user_id=from_user_id)
        user_id_set = set([
            fs.to_user_id
            for fs in friendships
        ])
        cache.set(key, user_id_set)
        return user_id_set

    @classmethod
    def has_followed(cls, from_user, to_user):
        return Friendship.objects.filter(
            from_user=from_user,
            to_user=to_user,
        ).exists()

    # less likely to have race condition
    @classmethod
    def invalidate_following_cache(cls, from_user_id):
        key = FOLLOWINGS_PATTERN.format(user_id=from_user_id)
        cache.delete(key)