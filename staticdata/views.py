import datetime

from rest_framework.response import Response
from staticdata.serializers import BaseEventSerializers
from staticdata.models import BaseEvent
from rest_framework import generics, status
from FeverCodeChallenge.utils import api_validate


class BaseEventList(generics.ListAPIView):
    serializer_class = BaseEventSerializers
    queryset = BaseEvent.objects.filter(sell_mode='online')

    def get_queryset(self):
        starts_at = api_validate(self.request, 'starts_at')
        ends_at = api_validate(self.request, 'ends_at')
        return self.queryset.filter(event__sell_from__gt=starts_at, event__sell_to__lt=ends_at)

    def get(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_queryset(), many=True)

        return Response({'data': {'events': serializer.data}, 'error': None})
