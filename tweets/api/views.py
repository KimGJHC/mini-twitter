from newsfeeds.services import NewsFeedService
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from tweets.api.serializers import (
    TweetSerializerForCreate,
    TweetSerializer,
    TweetSerializerForDetail,
)
from tweets.models import Tweet
from utils.decorators import required_params
from utils.paginations import EndlessPagination
from tweets.services import TweetService
from django.utils.decorators import method_decorator
from ratelimit.decorators import ratelimit

class TweetViewSet(viewsets.GenericViewSet):

    # API end point to let user create and list tweets
    queryset = Tweet.objects.all()
    serializer_class = TweetSerializerForCreate
    pagination_class = EndlessPagination

    # check permission to actions
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]

    @method_decorator(ratelimit(key='user_or_ip', rate='1/s', method='GET', block=True))
    def retrieve(self, request, *args, **kwargs):
        tweet = self.get_object()
        return Response(TweetSerializerForDetail(
            tweet,
            context={'request':request,}
        ).data)

    @required_params(params=['user_id'])
    @method_decorator(ratelimit(key='user_or_ip', rate='1/s', method='GET', block=True))
    def list(self, request):
        # we want to create composite index with user_id and created_at
        user_id = request.query_params['user_id']
        cached_tweets = TweetService.get_cached_tweets(user_id)
        page = self.paginator.paginate_cached_list(cached_tweets, request)
        if page is None:
            queryset = Tweet.objects.filter(user_id=user_id).order_by('-created_at')
            page = self.paginate_queryset(queryset)
        serializer = TweetSerializer(
            page,
            context={'request': request},
            many=True,
        )

        return self.get_paginated_response(serializer.data)

    @method_decorator(ratelimit(key='user', rate='1/s', method='POST', block=True))
    @method_decorator(ratelimit(key='user', rate='6/m', method='POST', block=True))
    def create(self, request):
        serializer = TweetSerializerForCreate(
            data=request.data,
            context={'request': request},
        )
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': "Please check input",
                'errors': serializer.errors,
            }, status=400)
        tweet = serializer.save()
        NewsFeedService.fanout_to_followers(tweet)
        return Response(TweetSerializer(tweet,context={'request':request}).data,
                        status=201,
                        )