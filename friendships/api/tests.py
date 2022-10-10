from friendships.models import Friendship
from rest_framework.test import APIClient
from testing.testcases import TestCase


FOLLOW_URL = '/api/friendships/{}/follow/'
UNFOLLOW_URL = '/api/friendships/{}/unfollow/'
FOLLOWERS_URL = '/api/friendships/{}/followers/'
FOLLOWINGS_URL = '/api/friendships/{}/followings/'


class FriendshipApiTests(TestCase):

    def setUp(self):
        self.anonymous_client = APIClient()

        self.kim = self.create_user('kim')
        self.kim_client = APIClient()
        self.kim_client.force_authenticate(self.kim)

        self.david = self.create_user('david')
        self.david_client = APIClient()
        self.david_client.force_authenticate(self.david)

        # create followings and followers for david
        for i in range(2):
            follower = self.create_user('david_follower{}'.format(i))
            Friendship.objects.create(from_user=follower, to_user=self.david)
        for i in range(3):
            following = self.create_user('david_following{}'.format(i))
            Friendship.objects.create(from_user=self.david, to_user=following)

    def test_follow(self):
        url = FOLLOW_URL.format(self.kim.id)

        # login first, then follow
        response = self.anonymous_client.post(url)
        self.assertEqual(response.status_code, 403)
        # use GET to follow
        response = self.david_client.get(url)
        self.assertEqual(response.status_code, 405)
        # cannot follow yourself
        response = self.kim_client.post(url)
        self.assertEqual(response.status_code, 400)
        # follow successfully
        response = self.david_client.post(url)
        self.assertEqual(response.status_code, 201)
        # duplicated follow
        response = self.david_client.post(url)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['duplicate'], True)
        # inverse follow
        count = Friendship.objects.count()
        response = self.kim_client.post(FOLLOW_URL.format(self.david.id))
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Friendship.objects.count(), count + 1)

    def test_unfollow(self):
        url = UNFOLLOW_URL.format(self.kim.id)

        # login first, then unfollow
        response = self.anonymous_client.post(url)
        self.assertEqual(response.status_code, 403)
        # cannot use get to unfollow
        response = self.david_client.get(url)
        self.assertEqual(response.status_code, 405)
        # cannot unfollow yourself
        response = self.kim_client.post(url)
        self.assertEqual(response.status_code, 400)
        # unfollow successfully
        Friendship.objects.create(from_user=self.david, to_user=self.kim)
        count = Friendship.objects.count()
        response = self.david_client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['deleted'], 1)
        self.assertEqual(Friendship.objects.count(), count - 1)
        # unfollow while not follow
        count = Friendship.objects.count()
        response = self.david_client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['deleted'], 0)
        self.assertEqual(Friendship.objects.count(), count)

    def test_followings(self):
        url = FOLLOWINGS_URL.format(self.david.id)
        # post is not allowed
        response = self.anonymous_client.post(url)
        self.assertEqual(response.status_code, 405)
        # get is ok
        response = self.anonymous_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['followings']), 3)
        # followings sorted by created_at desc
        ts0 = response.data['followings'][0]['created_at']
        ts1 = response.data['followings'][1]['created_at']
        ts2 = response.data['followings'][2]['created_at']
        self.assertEqual(ts0 > ts1, True)
        self.assertEqual(ts1 > ts2, True)
        self.assertEqual(
            response.data['followings'][0]['user']['username'],
            'david_following2',
        )
        self.assertEqual(
            response.data['followings'][1]['user']['username'],
            'david_following1',
        )
        self.assertEqual(
            response.data['followings'][2]['user']['username'],
            'david_following0',
        )

    def test_followers(self):
        url = FOLLOWERS_URL.format(self.david.id)
        # post is not allowed
        response = self.anonymous_client.post(url)
        self.assertEqual(response.status_code, 405)
        # get is ok
        response = self.anonymous_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['followers']), 2)
        # followers sorted by created_at desc
        ts0 = response.data['followers'][0]['created_at']
        ts1 = response.data['followers'][1]['created_at']
        self.assertEqual(ts0 > ts1, True)
        self.assertEqual(
            response.data['followers'][0]['user']['username'],
            'david_follower1',
        )
        self.assertEqual(
            response.data['followers'][1]['user']['username'],
            'david_follower0',
        )