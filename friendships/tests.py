from friendships.models import Friendship
from friendships.services import FriendshipService
from testing.testcases import TestCase


class FriendshipServiceTests(TestCase):

    def setUp(self):
        self.clear_cache()
        self.kim = self.create_user('kim')
        self.david = self.create_user('david')

    def test_get_followings(self):
        user1 = self.create_user('user1')
        user2 = self.create_user('user2')
        for to_user in [user1, user2, self.david]:
            Friendship.objects.create(from_user=self.kim, to_user=to_user)
        # no need of following line if we set up listener at model level (use signals)
        FriendshipService.invalidate_following_cache(self.kim.id)

        user_id_set = FriendshipService.get_following_user_id_set(self.kim.id)
        self.assertSetEqual(user_id_set, {user1.id, user2.id, self.david.id})

        Friendship.objects.filter(from_user=self.kim, to_user=self.david).delete()
        FriendshipService.invalidate_following_cache(self.kim.id)
        user_id_set = FriendshipService.get_following_user_id_set(self.kim.id)
        self.assertSetEqual(user_id_set, {user1.id, user2.id})
