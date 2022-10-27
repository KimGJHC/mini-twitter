from django.contrib.auth.models import User
from testing.testcases import TestCase
from tweets.models import (
    Tweet,
    TweetPhoto,
)
from tweets.constants import TweetPhotoStatus
from datetime import timedelta
from utils.time_helpers import utc_now
from utils.redis_client import RedisClient
from utils.redis_serializers import DjangoModelSerializer


class TweetTests(TestCase):

    def setUp(self):
        self.clear_cache()
        self.kim = self.create_user('kim')
        self.tweet = self.create_tweet(self.kim, content='Hello world!')


    def test_hours_to_now(self):
        admin = User.objects.create_user(username='admin')
        tweet = Tweet.objects.create(user=admin, content='Test tweet content!')
        tweet.created_at = utc_now() - timedelta(hours=10)
        tweet.save()
        self.assertEqual(tweet.hours_to_now, 10)

    def test_like_set(self):
        self.create_like(self.kim, self.tweet)
        self.assertEqual(self.tweet.like_set.count(), 1)

        self.create_like(self.kim, self.tweet)
        self.assertEqual(self.tweet.like_set.count(), 1)

        david = self.create_user('david')
        self.create_like(david, self.tweet)
        self.assertEqual(self.tweet.like_set.count(), 2)


    def test_create_photo(self):
        photo = TweetPhoto.objects.create(
            tweet=self.tweet,
            user=self.kim,
        )
        self.assertEqual(photo.user, self.kim)
        self.assertEqual(photo.status, TweetPhotoStatus.PENDING)
        self.assertEqual(self.tweet.tweetphoto_set.count(), 1)

    def test_cache_tweet_in_redis(self):
        tweet = self.create_tweet(self.kim)
        conn = RedisClient.get_connection()
        serialized_data = DjangoModelSerializer.serialize(tweet)
        conn.set(f'tweet:{tweet.id}', serialized_data)
        data = conn.get(f'tweet:not_exists')
        self.assertEqual(data, None)

        data = conn.get(f'tweet:{tweet.id}')
        cached_tweet = DjangoModelSerializer.deserialize(data)
        self.assertEqual(tweet, cached_tweet)
