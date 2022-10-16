from django.db import models
from django.contrib.auth.models import User
from tweets.models import Tweet

class NewsFeed(models.Model):
    # user is the follower of the owner of tweet
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    tweet = models.ForeignKey(Tweet, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # get user's news feed ordered by created at
        index_together = (('user', 'created_at'),)
        # one user can only view on particular tweet
        unique_together = (('user', 'tweet'),)
        ordering = ('-created_at',)

    def __str__(self):
        return f'{self.created_at} inbox of {self.user}: {self.tweet}'