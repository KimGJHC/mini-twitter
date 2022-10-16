from comments.models import Comment
from django.utils import timezone
from rest_framework.test import APIClient
from testing.testcases import TestCase


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

    def test_destroy(self):
        comment = self.create_comment(self.kim, self.tweet)
        url = '{}{}/'.format(COMMENT_URL, comment.id)

        # anonymous cannot delete
        response = self.anonymous_client.delete(url)
        self.assertEqual(response.status_code, 403)

        # only can be deleted by owner
        response = self.david_client.delete(url)
        self.assertEqual(response.status_code, 403)

        # owner successfully delete
        count = Comment.objects.count()
        response = self.kim_client.delete(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Comment.objects.count(), count - 1)

    def test_update(self):
        comment = self.create_comment(self.kim, self.tweet, 'original')
        another_tweet = self.create_tweet(self.david)
        url = '{}{}/'.format(COMMENT_URL, comment.id)

        # anonymoust cannot update
        response = self.anonymous_client.put(url, {'content': 'new'})
        self.assertEqual(response.status_code, 403)
        # only owner can update
        response = self.david_client.put(url, {'content': 'new'})
        self.assertEqual(response.status_code, 403)
        comment.refresh_from_db()
        self.assertNotEqual(comment.content, 'new')
        # can only update content
        before_updated_at = comment.updated_at
        before_created_at = comment.created_at
        now = timezone.now()
        response = self.kim_client.put(url, {
            'content': 'new',
            'user_id': self.david.id,
            'tweet_id': another_tweet.id,
            'created_at': now,
        })
        self.assertEqual(response.status_code, 200)
        comment.refresh_from_db()
        self.assertEqual(comment.content, 'new')
        self.assertEqual(comment.user, self.kim)
        self.assertEqual(comment.tweet, self.tweet)
        self.assertEqual(comment.created_at, before_created_at)
        self.assertNotEqual(comment.created_at, now)
        self.assertNotEqual(comment.updated_at, before_updated_at)