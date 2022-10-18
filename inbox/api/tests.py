from notifications.models import Notification
from testing.testcases import TestCase


COMMENT_URL = '/api/comments/'
LIKE_URL = '/api/likes/'


class NotificationTests(TestCase):

    def setUp(self):
        self.kim, self.kim_client = self.create_user_and_client('kim')
        self.david, self.david_client = self.create_user_and_client('dong')
        self.david_tweet = self.create_tweet(self.david)

    def test_comment_create_api_trigger_notification(self):
        self.assertEqual(Notification.objects.count(), 0)
        self.kim_client.post(COMMENT_URL, {
            'tweet_id': self.david_tweet.id,
            'content': 'a ha',
        })
        self.assertEqual(Notification.objects.count(), 1)

    def test_like_create_api_trigger_notification(self):
        self.assertEqual(Notification.objects.count(), 0)
        self.kim_client.post(LIKE_URL, {
            'content_type': 'tweet',
            'object_id': self.david_tweet.id,
        })
        self.assertEqual(Notification.objects.count(), 1)