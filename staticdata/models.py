from django.db import models
import logging
import uuid


class BaseEvent(models.Model):
    SELL_MODE_CHOICES = (('online', 'online'),
                         ('offline', 'offline'))
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    base_event_id = models.IntegerField(unique=True)
    title = models.CharField(max_length=150)
    sell_mode = models.CharField(max_length=40, choices=SELL_MODE_CHOICES)

    def __str__(self):
        return self.title


class Zone(models.Model):
    zone_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Event(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event_id = models.IntegerField(unique=True)
    event_date = models.DateTimeField()
    base_event = models.ForeignKey(BaseEvent, on_delete=models.CASCADE)
    sell_from = models.DateTimeField()
    sell_to = models.DateTimeField()
    zones = models.ManyToManyField(Zone, through='EventZone')
    sold_out = models.BooleanField()

    def __str__(self):
        return '%s (%s - %s)' % (self.base_event.title, self.sell_from.strftime('%Y-%m-%d %H:%M:%S'), self.sell_to.strftime('%Y-%m-%d %H:%M:%S'))


class EventZone(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    capacity = models.IntegerField()
    numbered = models.BooleanField()


class Log(models.Model):
    date = models.DateTimeField(auto_now_add=True, db_index=True)
    application = models.CharField(max_length=32, db_index=True)
    level = models.IntegerField(choices=((logging.DEBUG, "Debug"),
                                         (logging.INFO, "Info"),
                                         (logging.WARNING, "Warning"),
                                         (logging.ERROR, "Error"),
                                         (logging.CRITICAL, "Critical")))
    text = models.TextField()

    def __str__(self):
        return self.application

