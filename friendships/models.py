from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_delete
from utils.memcached_helper import MemcachedHelper
from friendships.listeners import friendship_changed

class Friendship(models.Model):

    from_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='following_friendship_set',
    )

    to_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='follower_friendship_set',
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        index_together = (
            # given a user, retrieve all users he or she follows, the newest first
            ('from_user_id', 'created_at'),
            # given a user, retrieve all users follow him or her, the newest first
            ('to_user_id', 'created_at'),
        )

        # each pair of friendship will only be stored once
        # deal with multiple clicking
        unique_together = (('from_user_id', 'to_user_id'),)

    def __str__(self):
        return '{} followed {}'.format(self.from_user_id, self.to_user_id)

    @property
    def cached_from_user(self):
        return MemcachedHelper.get_object_through_cache(User, self.from_user_id)

    @property
    def cached_to_user(self):
        return MemcachedHelper.get_object_through_cache(User, self.to_user_id)

pre_delete.connect(friendship_changed, sender=Friendship)
post_save.connect(friendship_changed, sender=Friendship)

