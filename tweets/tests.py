from django.contrib.auth.models import User
from testing.testcases import TestCase
from tweets.models import Tweet
from datetime import timedelta
from utils.time_helpers import utc_now


class TweetTests(TestCase):

    def setUp(self):
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
