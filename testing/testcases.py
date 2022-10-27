from django.test import TestCase as DjangoTestCase
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import ContentType
from django.core.cache import caches
from tweets.models import Tweet
from comments.models import Comment
from likes.models import Like
from newsfeeds.models import NewsFeed
from rest_framework.test import APIClient
from utils.redis_client import RedisClient


class TestCase(DjangoTestCase):
    def clear_cache(self):
        # django test will roll back db but not cache
        caches['testing'].clear()
        RedisClient.clear()

    @property
    def anonymous_client(self):
        # no need to new a client instance everytime
        if hasattr(self, '_anonymous_client'):
            return self._anonymous_client
        self._anonymous_client = APIClient()
        return self._anonymous_client

    def create_user(self, username, email=None, password=None):
        if password is None:
            password = 'generic password'
        if email is None:
            email = f'{username}@gmail.com'

        return User.objects.create_user(username, email, password)

    def create_tweet(self, user, content=None):
        if content is None:
            content = 'default tweet content'
        return Tweet.objects.create(user=user, content=content)

    def create_comment(self, user, tweet, content=None):
        if content is None:
            content = 'default comment content'
        return Comment.objects.create(user=user, tweet=tweet, content=content)

    def create_like(self, user, target):
        """
        :param user:
        :param target: comment or tweet
        :return:
        """
        instance, _ = Like.objects.get_or_create(
            content_type=ContentType.objects.get_for_model(target.__class__),
            object_id=target.id,
            user=user,
        )
        return instance

    def create_user_and_client(self, *args, **kwargs):
        user = self.create_user(*args, **kwargs)
        client = APIClient()
        client.force_authenticate(user)
        return user, client


    def create_newsfeed(self, user, tweet):
        return NewsFeed.objects.create(user=user, tweet=tweet)