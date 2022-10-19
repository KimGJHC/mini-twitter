from notifications.models import Notification
from testing.testcases import TestCase


COMMENT_URL = '/api/comments/'
LIKE_URL = '/api/likes/'
NOTIFICATION_URL = '/api/notifications/'


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


class NotificationApiTests(TestCase):

    def setUp(self):
        self.kim, self.kim_client = self.create_user_and_client('kim')
        self.david, self.david_client = self.create_user_and_client('david')
        self.kim_tweet = self.create_tweet(self.kim)

    def test_unread_count(self):
        self.david_client.post(LIKE_URL, {
            'content_type': 'tweet',
            'object_id': self.kim_tweet.id,
        })

        url = '/api/notifications/unread-count/'
        response = self.kim_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['unread_count'], 1)

        comment = self.create_comment(self.kim, self.kim_tweet)
        self.david_client.post(LIKE_URL, {
            'content_type': 'comment',
            'object_id': comment.id,
        })
        response = self.kim_client.get(url)
        self.assertEqual(response.data['unread_count'], 2)

    def test_mark_all_as_read(self):
        self.david_client.post(LIKE_URL, {
            'content_type': 'tweet',
            'object_id': self.kim_tweet.id,
        })
        comment = self.create_comment(self.kim, self.kim_tweet)
        self.david_client.post(LIKE_URL, {
            'content_type': 'comment',
            'object_id': comment.id,
        })

        unread_url = '/api/notifications/unread-count/'
        response = self.kim_client.get(unread_url)
        self.assertEqual(response.data['unread_count'], 2)

        mark_url = '/api/notifications/mark-all-as-read/'
        response = self.kim_client.get(mark_url)
        self.assertEqual(response.status_code, 405)
        response = self.kim_client.post(mark_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['marked_count'], 2)
        response = self.kim_client.get(unread_url)
        self.assertEqual(response.data['unread_count'], 0)

    def test_list(self):
        self.david_client.post(LIKE_URL, {
            'content_type': 'tweet',
            'object_id': self.kim_tweet.id,
        })
        comment = self.create_comment(self.kim, self.kim_tweet)
        self.david_client.post(LIKE_URL, {
            'content_type': 'comment',
            'object_id': comment.id,
        })

        # anonymous user cannot get notification
        response = self.anonymous_client.get(NOTIFICATION_URL)
        self.assertEqual(response.status_code, 403)
        # david initialize with no notification
        response = self.david_client.get(NOTIFICATION_URL)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 0)
        # kim can see 2 notifications
        response = self.kim_client.get(NOTIFICATION_URL)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 2)
        # kim get 1 unread notification
        notification = self.kim.notifications.first()
        notification.unread = False
        notification.save()
        response = self.kim_client.get(NOTIFICATION_URL)
        self.assertEqual(response.data['count'], 2)
        response = self.kim_client.get(NOTIFICATION_URL, {'unread': True})
        self.assertEqual(response.data['count'], 1)
        response = self.kim_client.get(NOTIFICATION_URL, {'unread': False})
        self.assertEqual(response.data['count'], 1)