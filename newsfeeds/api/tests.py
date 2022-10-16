from newsfeeds.models import NewsFeed
from friendships.models import Friendship
from rest_framework.test import APIClient
from testing.testcases import TestCase


NEWSFEEDS_URL = '/api/newsfeeds/'
POST_TWEETS_URL = '/api/tweets/'
FOLLOW_URL = '/api/friendships/{}/follow/'

class NewsFeedApiTests(TestCase):

    def setUp(self):
        self.kim = self.create_user('kim')
        self.kim_client = APIClient()
        self.kim_client.force_authenticate(self.kim)

        self.david = self.create_user('david')
        self.david_client = APIClient()
        self.david_client.force_authenticate(self.david)

        # create followings and followers for kim
        for i in range(2):
            follower = self.create_user('kim_follower{}'.format(i))
            Friendship.objects.create(from_user=follower, to_user=self.david)
        for i in range(3):
            following = self.create_user('david_following{}'.format(i))
            Friendship.objects.create(from_user=self.david, to_user=following)

    def test_list(self):
        # require login
        response = self.anonymous_client.get(NEWSFEEDS_URL)
        self.assertEqual(response.status_code, 403)
        # need to use GET
        response = self.kim_client.post(NEWSFEEDS_URL)
        self.assertEqual(response.status_code, 405)
        # no newsfeeds initially
        response = self.kim_client.get(NEWSFEEDS_URL)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['newsfeeds']), 0)
        # tweet owner can see own tweet in newsfeeds
        self.kim_client.post(POST_TWEETS_URL, {'content': 'Hello World'})
        response = self.kim_client.get(NEWSFEEDS_URL)
        self.assertEqual(len(response.data['newsfeeds']), 1)
        # followings can see follower's tweet in newsfeeds
        self.kim_client.post(FOLLOW_URL.format(self.david.id))
        response = self.david_client.post(POST_TWEETS_URL, {
            'content': 'Hello Twitter',
        })
        posted_tweet_id = response.data['id']
        response = self.kim_client.get(NEWSFEEDS_URL)
        self.assertEqual(len(response.data['newsfeeds']), 2)
        self.assertEqual(response.data['newsfeeds'][0]['tweet']['id'], posted_tweet_id)
