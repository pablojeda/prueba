import os
import sys
import django
import requests
from xml.etree import ElementTree as ET

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root not in sys.path:
    sys.path.append(root)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "FeverCodeChallenge.development")
django.setup()

from staticdata.models import Event, BaseEvent, Zone, EventZone
from FeverCodeChallenge.utils import get_logger

REQUEST_URL = 'https://provider.code-challenge.feverup.com/api/events'


if __name__ == '__main__':
    logger = get_logger('get_events')
    logger.info('Starting process')
    response = requests.get(REQUEST_URL)
    xml_content = ET.fromstring(response.content)
    for base_event_xml in xml_content[0]:
        try:
            defaults = {
                'title': base_event_xml.get('title'),
                'sell_mode': base_event_xml.get('sell_mode')
            }
            base_event, created = BaseEvent.objects.update_or_create(base_event_id=base_event_xml.get('base_event_id'), defaults=defaults)
            if created:
                logger.info('Created new Base event: %s' % base_event)
            event_xml = base_event_xml[0]

            defaults = {
                'event_date': event_xml.get('event_date'),
                'base_event': base_event,
                'sell_from': event_xml.get('sell_from'),
                'sell_to': event_xml.get('sell_to'),
                'sold_out': event_xml.get('sold_out') == 'true'
            }
            event, created = Event.objects.update_or_create(event_id=event_xml.get('event_id'), defaults=defaults)
            if created:
                logger.info('Created new Event: %s' % event)
            for zone_xml in event_xml:
                try:
                    defaults = {
                        'name': zone_xml.get('name')
                    }
                    zone, created = Zone.objects.update_or_create(zone_id=zone_xml.get('zone_id'), defaults=defaults)
                    if created:
                        logger.info('Created new Zone: %s' % zone)

                    defaults = {
                        'price': float(zone_xml.get('price')),
                        'capacity': int(zone_xml.get('capacity')),
                        'numbered': zone_xml.get('numbered') == 'true'
                    }
                    event_zone, _ = EventZone.objects.update_or_create(zone=zone, event=event, defaults=defaults)
                except Exception as e:
                    logger.error('The Zone with id %s could not be processed: %s' % (zone_xml.get('zone_id'), e))

        except Exception as e:
            logger.error('The Base event with id %s could not be processed: %s' % (base_event_xml.get('base_event_id'), e))

    logger.info('Finished process')
