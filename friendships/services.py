# service is interacting with data model

from friendships.models import Friendship


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