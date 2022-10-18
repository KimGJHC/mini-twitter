from django.contrib.contenttypes.fields import ContentType
from notifications.signals import notify
from tweets.models import Tweet
from comments.models import Comment


class NotificationService(object):

    @classmethod
    def send_like_notification(cls, like):
        target = like.content_object
        # do not notify if the like creator is the owner of the liked object
        if like.user == target.user:
            return

        # signals can be replaced by services to centralize related logics
        if like.content_type == ContentType.objects.get_for_model(Tweet):
            notify.send(
                like.user,
                recipient=target.user,
                verb='liked your tweet',
                target=target,
            )
        elif like.content_type == ContentType.objects.get_for_model(Comment):
            notify.send(
                like.user,
                recipient=target.user,
                verb='liked your comment',
                target=target,
            )
    @classmethod
    def send_comment_notification(cls, comment):
        # do not notify if the comment creator is the owner of the tweet
        if comment.user == comment.tweet.user:
            return
        notify.send(
            comment.user,
            recipient=comment.tweet.user,
            verb='commented on your tweet',
            target=comment.tweet,
        )
