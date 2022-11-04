from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from newsfeeds.models import NewsFeed
from newsfeeds.api.serializers import NewsFeedSerializer
from utils.paginations import EndlessPagination
from newsfeeds.services import NewsFeedService
from django.utils.decorators import method_decorator
from ratelimit.decorators import ratelimit

class NewsFeedViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    pagination_class = EndlessPagination

    @method_decorator(ratelimit(key='user', rate='1/s', method='GET', block=True))
    def list(self, request):
        cached_newsfeeds = NewsFeedService.get_cached_newsfeeds(request.user.id)
        page = self.paginator.paginate_cached_list(cached_newsfeeds, request)
        if page is None:
            queryset = NewsFeed.objects.filter(user=request.user)
            page = self.paginate_queryset(queryset)
        serializer = NewsFeedSerializer(
            page,
            context={'request':request},
            many=True,
        )
        return self.get_paginated_response(serializer.data)