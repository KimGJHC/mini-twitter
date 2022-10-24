from newsfeeds.models import NewsFeed
from friendships.models import Friendship
from rest_framework.test import APIClient
from testing.testcases import TestCase
from utils.paginations import EndlessPagination


NEWSFEEDS_URL = '/api/newsfeeds/'
POST_TWEETS_URL = '/api/tweets/'
FOLLOW_URL = '/api/friendships/{}/follow/'

class NewsFeedApiTests(TestCase):

    def setUp(self):
        self.clear_cache()
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
        self.assertEqual(len(response.data['results']), 0)
        # tweet owner can see own tweet in newsfeeds
        self.kim_client.post(POST_TWEETS_URL, {'content': 'Hello World'})
        response = self.kim_client.get(NEWSFEEDS_URL)
        self.assertEqual(len(response.data['results']), 1)
        # followings can see follower's tweet in newsfeeds
        self.kim_client.post(FOLLOW_URL.format(self.david.id))
        response = self.david_client.post(POST_TWEETS_URL, {
            'content': 'Hello Twitter',
        })
        posted_tweet_id = response.data['id']
        response = self.kim_client.get(NEWSFEEDS_URL)
        self.assertEqual(len(response.data['results']), 2)
        self.assertEqual(response.data['results'][0]['tweet']['id'], posted_tweet_id)

    def test_pagination(self):
        page_size = EndlessPagination.page_size
        followed_user = self.create_user('followed')
        newsfeeds = []
        for i in range(page_size * 2):
            tweet = self.create_tweet(followed_user)
            newsfeed = self.create_newsfeed(user=self.kim, tweet=tweet)
            newsfeeds.append(newsfeed)

        newsfeeds = newsfeeds[::-1]

        # pull the first page
        response = self.kim_client.get(NEWSFEEDS_URL)
        self.assertEqual(response.data['has_next_page'], True)
        self.assertEqual(len(response.data['results']), page_size)
        self.assertEqual(response.data['results'][0]['id'], newsfeeds[0].id)
        self.assertEqual(response.data['results'][1]['id'], newsfeeds[1].id)
        self.assertEqual(
            response.data['results'][page_size - 1]['id'],
            newsfeeds[page_size - 1].id,
        )

        # pull the second page
        response = self.kim_client.get(
            NEWSFEEDS_URL,
            {'created_at__lt': newsfeeds[page_size - 1].created_at},
        )
        self.assertEqual(response.data['has_next_page'], False)
        results = response.data['results']
        self.assertEqual(len(results), page_size)
        self.assertEqual(results[0]['id'], newsfeeds[page_size].id)
        self.assertEqual(results[1]['id'], newsfeeds[page_size + 1].id)
        self.assertEqual(
            results[page_size - 1]['id'],
            newsfeeds[2 * page_size - 1].id,
        )

        # pull the latest newsfeeds
        response = self.kim_client.get(
            NEWSFEEDS_URL,
            {'created_at__gt': newsfeeds[0].created_at},
        )
        self.assertEqual(response.data['has_next_page'], False)
        self.assertEqual(len(response.data['results']), 0)

        tweet = self.create_tweet(followed_user)
        new_newsfeed = self.create_newsfeed(user=self.kim, tweet=tweet)

        response = self.kim_client.get(
            NEWSFEEDS_URL,
            {'created_at__gt': newsfeeds[0].created_at},
        )
        self.assertEqual(response.data['has_next_page'], False)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['id'], new_newsfeed.id)

    def test_user_cache(self):
        profile = self.david.profile
        profile.nickname = 'david2'
        profile.save()

        self.assertEqual(self.kim.username, 'kim')
        self.create_newsfeed(self.david, self.create_tweet(self.kim))
        self.create_newsfeed(self.david, self.create_tweet(self.david))

        response = self.david_client.get(NEWSFEEDS_URL)
        results = response.data['results']
        self.assertEqual(results[0]['tweet']['user']['username'], 'david')
        self.assertEqual(results[0]['tweet']['user']['nickname'], 'david2')
        self.assertEqual(results[1]['tweet']['user']['username'], 'kim')

        self.kim.username = 'kim2'
        self.kim.save()
        profile.nickname = 'david2333'
        profile.save()

        response = self.david_client.get(NEWSFEEDS_URL)
        results = response.data['results']
        self.assertEqual(results[0]['tweet']['user']['username'], 'david')
        self.assertEqual(results[0]['tweet']['user']['nickname'], 'david2333')
        self.assertEqual(results[1]['tweet']['user']['username'], 'kim2')

    def test_tweet_cache(self):
        tweet = self.create_tweet(self.kim, 'content1')
        self.create_newsfeed(self.david, tweet)
        response = self.david_client.get(NEWSFEEDS_URL)
        results = response.data['results']
        self.assertEqual(results[0]['tweet']['user']['username'], 'kim')
        self.assertEqual(results[0]['tweet']['content'], 'content1')

        # update username
        self.kim.username = 'kim2'
        self.kim.save()
        response = self.david_client.get(NEWSFEEDS_URL)
        results = response.data['results']
        self.assertEqual(results[0]['tweet']['user']['username'], 'kim2')

        # update content
        tweet.content = 'content2'
        tweet.save()
        response = self.david_client.get(NEWSFEEDS_URL)
        results = response.data['results']
        self.assertEqual(results[0]['tweet']['content'], 'content2')
