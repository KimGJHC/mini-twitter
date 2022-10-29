from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from newsfeeds.models import NewsFeed
from newsfeeds.api.serializers import NewsFeedSerializer
from utils.paginations import EndlessPagination
from newsfeeds.services import NewsFeedService

class NewsFeedViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    pagination_class = EndlessPagination

    def list(self, request):
        queryset = NewsFeedService.get_cached_newsfeeds(request.user.id)
        page = self.paginate_queryset(queryset)
        serializer = NewsFeedSerializer(
            page,
            context={'request':request},
            many=True,
        )
        return self.get_paginated_response(serializer.data)