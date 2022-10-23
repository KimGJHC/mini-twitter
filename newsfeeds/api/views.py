from rest_framework import viewsets, status
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from newsfeeds.models import NewsFeed
from newsfeeds.api.serializers import NewsFeedSerializer
from utils.paginations import EndlessPagination

class NewsFeedViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    pagination_class = EndlessPagination

    def list(self, request):
        queryset = NewsFeed.objects.filter(user=self.request.user)
        page = self.paginate_queryset(queryset)
        serializer = NewsFeedSerializer(page,
                                        context={'request':request},
                                        many=True,
                                        )
        return self.get_paginated_response(serializer.data)