
from django.contrib import admin
from django.urls import include, path
from rest_framework import routers
from accounts.api.views import UserViewSet, AccountViewSet
from tweets.api.views import TweetViewSet
from friendships.api.views import FriendshipViewSet
from newsfeeds.api.views import NewsFeedViewSet

# router maps api/users to viewset
router = routers.DefaultRouter()
router.register(r'api/users', UserViewSet)
router.register(r'api/accounts', AccountViewSet, basename='accounts')
router.register(r'api/tweets', TweetViewSet, basename='tweets')
router.register(r'api/friendships', FriendshipViewSet, basename='friendships')
router.register(r'api/newsfeeds', NewsFeedViewSet, basename='newsfeeds')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)), # for front page view
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]
