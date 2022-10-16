from testing.testcases import TestCase


class CommentModelTests(TestCase):

    def setUp(self):
        self.kim = self.create_user('kim')
        self.tweet = self.create_tweet(self.kim)
        self.comment = self.create_comment(self.kim, self.tweet)

    def test_comment(self):
        user = self.create_user('david')
        tweet = self.create_tweet(user)
        comment = self.create_comment(user, tweet)
        self.assertNotEqual(comment.__str__(), None)

    def test_like_set(self):
        self.create_like(self.kim, self.comment)
        self.assertEqual(self.comment.like_set.count(), 1)

        self.create_like(self.kim, self.comment)
        self.assertEqual(self.comment.like_set.count(), 1)

        david = self.create_user('david')
        self.create_like(david, self.comment)
        self.assertEqual(self.comment.like_set.count(), 2)