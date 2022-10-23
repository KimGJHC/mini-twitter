from friendships.models import Friendship
from utils.paginations import FriendshipPagination
from rest_framework.test import APIClient
from testing.testcases import TestCase


FOLLOW_URL = '/api/friendships/{}/follow/'
UNFOLLOW_URL = '/api/friendships/{}/unfollow/'
FOLLOWERS_URL = '/api/friendships/{}/followers/'
FOLLOWINGS_URL = '/api/friendships/{}/followings/'


class FriendshipApiTests(TestCase):

    def setUp(self):
        self.kim = self.create_user('kim')
        self.kim_client = APIClient()
        self.kim_client.force_authenticate(self.kim)

        self.david = self.create_user('david')
        self.david_client = APIClient()
        self.david_client.force_authenticate(self.david)

        # create results and followers for david
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

    def test_results(self):
        url = FOLLOWINGS_URL.format(self.david.id)
        # post is not allowed
        response = self.anonymous_client.post(url)
        self.assertEqual(response.status_code, 405)
        # get is ok
        response = self.anonymous_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 3)
        # results sorted by created_at desc
        ts0 = response.data['results'][0]['created_at']
        ts1 = response.data['results'][1]['created_at']
        ts2 = response.data['results'][2]['created_at']
        self.assertEqual(ts0 > ts1, True)
        self.assertEqual(ts1 > ts2, True)
        self.assertEqual(
            response.data['results'][0]['user']['username'],
            'david_following2',
        )
        self.assertEqual(
            response.data['results'][1]['user']['username'],
            'david_following1',
        )
        self.assertEqual(
            response.data['results'][2]['user']['username'],
            'david_following0',
        )

    def test_results(self):
        url = FOLLOWERS_URL.format(self.david.id)
        # post is not allowed
        response = self.anonymous_client.post(url)
        self.assertEqual(response.status_code, 405)
        # get is ok
        response = self.anonymous_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 2)
        # results sorted by created_at desc
        ts0 = response.data['results'][0]['created_at']
        ts1 = response.data['results'][1]['created_at']
        self.assertEqual(ts0 > ts1, True)
        self.assertEqual(
            response.data['results'][0]['user']['username'],
            'david_follower1',
        )
        self.assertEqual(
            response.data['results'][1]['user']['username'],
            'david_follower0',
        )


    def test_followers_pagination(self):
        max_page_size = FriendshipPagination.max_page_size
        page_size = FriendshipPagination.page_size
        for i in range(page_size * 2):
            follower = self.create_user('kim_follower{}'.format(i))
            Friendship.objects.create(from_user=follower, to_user=self.kim)
            if follower.id % 2 == 0:
                Friendship.objects.create(from_user=self.david, to_user=follower)

        url = FOLLOWERS_URL.format(self.kim.id)
        self._test_friendship_pagination(url, page_size, max_page_size)

        # anonymous hasn't followed any users
        response = self.anonymous_client.get(url, {'page': 1})
        for result in response.data['results']:
            self.assertEqual(result['has_followed'], False)

        # david has followed users with even id
        response = self.david_client.get(url, {'page': 1})
        for result in response.data['results']:
            has_followed = (result['user']['id'] % 2 == 0)
            self.assertEqual(result['has_followed'], has_followed)

    def test_followings_pagination(self):
        max_page_size = FriendshipPagination.max_page_size
        page_size = FriendshipPagination.page_size
        for i in range(page_size * 2):
            following = self.create_user('kim_following{}'.format(i))
            Friendship.objects.create(from_user=self.kim, to_user=following)
            if following.id % 2 == 0:
                Friendship.objects.create(from_user=self.david, to_user=following)

        url = FOLLOWINGS_URL.format(self.kim.id)
        self._test_friendship_pagination(url, page_size, max_page_size)

        # anonymous hasn't followed any users
        response = self.anonymous_client.get(url, {'page': 1})
        for result in response.data['results']:
            self.assertEqual(result['has_followed'], False)

        # david has followed users with even id
        response = self.david_client.get(url, {'page': 1})
        for result in response.data['results']:
            has_followed = (result['user']['id'] % 2 == 0)
            self.assertEqual(result['has_followed'], has_followed)

        # kim has followed all his following users
        response = self.kim_client.get(url, {'page': 1})
        for result in response.data['results']:
            self.assertEqual(result['has_followed'], True)

    def _test_friendship_pagination(self, url, page_size, max_page_size):
        response = self.anonymous_client.get(url, {'page': 1})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), page_size)
        self.assertEqual(response.data['total_pages'], 2)
        self.assertEqual(response.data['total_results'], page_size * 2)
        self.assertEqual(response.data['page_number'], 1)
        self.assertEqual(response.data['has_next_page'], True)

        response = self.anonymous_client.get(url, {'page': 2})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), page_size)
        self.assertEqual(response.data['total_pages'], 2)
        self.assertEqual(response.data['total_results'], page_size * 2)
        self.assertEqual(response.data['page_number'], 2)
        self.assertEqual(response.data['has_next_page'], False)

        response = self.anonymous_client.get(url, {'page': 3})
        self.assertEqual(response.status_code, 404)

        # test user can not customize page_size exceeds max_page_size
        response = self.anonymous_client.get(url, {'page': 1, 'size': max_page_size + 1})
        self.assertEqual(len(response.data['results']), max_page_size)
        self.assertEqual(response.data['total_pages'], 2)
        self.assertEqual(response.data['total_results'], page_size * 2)
        self.assertEqual(response.data['page_number'], 1)
        self.assertEqual(response.data['has_next_page'], True)

        # test user can customize page size by param size
        response = self.anonymous_client.get(url, {'page': 1, 'size': 2})
        self.assertEqual(len(response.data['results']), 2)
        self.assertEqual(response.data['total_pages'], page_size)
        self.assertEqual(response.data['total_results'], page_size * 2)
        self.assertEqual(response.data['page_number'], 1)
        self.assertEqual(response.data['has_next_page'], True)