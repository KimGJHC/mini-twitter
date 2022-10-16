from friendships.services import FriendshipService
from newsfeeds.models import NewsFeed

class NewsFeedService(object):
    # service usually has class method

    @classmethod
    def fanout_to_followers(cls, tweet):
        # do not use for + query!!!
        # use bulk_create
        newsfeeds = [
            NewsFeed(user=follower, tweet=tweet)
            for follower in FriendshipService.get_followers(tweet.user)
        ]
        newsfeeds.append(NewsFeed(user=tweet.user, tweet=tweet))
        NewsFeed.objects.bulk_create(newsfeeds)