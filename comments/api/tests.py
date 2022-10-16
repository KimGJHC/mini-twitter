from testing.testcases import TestCase
from rest_framework.test import APIClient


COMMENT_URL = '/api/comments/'


class CommentApiTests(TestCase):

    def setUp(self):
        self.kim = self.create_user('kim')
        self.kim_client = APIClient()
        self.kim_client.force_authenticate(self.kim)
        self.david = self.create_user('david')
        self.david_client = APIClient()
        self.david_client.force_authenticate(self.david)

        self.tweet = self.create_tweet(self.kim)

    def test_create(self):
        # anonymous user cannot create comments
        response = self.anonymous_client.post(COMMENT_URL)
        self.assertEqual(response.status_code, 403)

        # post need to have params
        response = self.kim_client.post(COMMENT_URL)
        self.assertEqual(response.status_code, 400)

        # post need content
        response = self.kim_client.post(COMMENT_URL, {'tweet_id': self.tweet.id})
        self.assertEqual(response.status_code, 400)

        # post need tweet_id
        response = self.kim_client.post(COMMENT_URL, {'content': '1'})
        self.assertEqual(response.status_code, 400)

        # content limit
        response = self.kim_client.post(COMMENT_URL, {
            'tweet_id': self.tweet.id,
            'content': '1' * 141,
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual('content' in response.data['errors'], True)

        # successful post
        response = self.kim_client.post(COMMENT_URL, {
            'tweet_id': self.tweet.id,
            'content': '1',
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['user']['id'], self.kim.id)
        self.assertEqual(response.data['tweet_id'], self.tweet.id)
        self.assertEqual(response.data['content'], '1')