from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.fields import ContentType
from utils.memcached_helper import MemcachedHelper
from django.db.models.signals import pre_delete, post_save
from likes.listeners import incr_likes_count, decr_likes_count

class Like(models.Model):
    object_id = models.PositiveIntegerField()
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.SET_NULL,
        null=True,
    )
    # implement like.content_object based on type and id
    content_object = GenericForeignKey('content_type', 'object_id')
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        index_together = (('content_type', 'object_id', 'created_at'),
                          ('user', 'content_type', 'created_at'),)
        unique_together = (('user', 'content_type', 'object_id'),)

    def __str__(self):
        return '{} - {} liked {} {}'.format(
            self.created_at,
            self.user,
            self.content_type,
            self.object_id,
        )
    @property
    def cached_user(self):
        return MemcachedHelper.get_object_through_cache(User, self.user_id)

pre_delete.connect(decr_likes_count, sender=Like)
post_save.connect(incr_likes_count, sender=Like)