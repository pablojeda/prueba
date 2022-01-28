from rest_framework import serializers
from staticdata.models import BaseEvent


class BaseEventSerializers(serializers.ModelSerializer):
    start_date = serializers.SerializerMethodField()
    start_time = serializers.SerializerMethodField()
    end_date = serializers.SerializerMethodField()
    end_time = serializers.SerializerMethodField()
    min_price = serializers.SerializerMethodField()
    max_price = serializers.SerializerMethodField()

    def get_start_date(self, obj):
        min_event = obj.event_set.all().order_by('sell_from').last()

        return min_event.sell_from.strftime('%Y-%m-%d') if min_event else 'N/A'

    def get_start_time(self, obj):
        min_event = obj.event_set.all().order_by('sell_from').last()

        return min_event.sell_from.strftime('%H:%M:%S') if min_event else 'N/A'

    def get_end_date(self, obj):
        max_event = obj.event_set.all().order_by('sell_to').last()

        return max_event.sell_to.strftime('%Y-%m-%d') if max_event else 'N/A'

    def get_end_time(self, obj):
        max_event = obj.event_set.all().order_by('sell_to').last()

        return max_event.event_date.strftime('%H:%M:%S') if max_event else 'N/A'

    def get_min_price(self, obj):
        try:
            value = min(obj.event_set.all().values_list("eventzone__price", flat=True))
        except ValueError:
            value = 'N/A'

        return value or 'N/A'

    def get_max_price(self, obj):
        try:
            value = max(obj.event_set.all().values_list("eventzone__price", flat=True))
        except ValueError:
            value = 'N/A'

        return value or 'N/A'

    class Meta:
        model = BaseEvent
        exclude = ['base_event_id', 'sell_mode']
