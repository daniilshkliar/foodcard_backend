import pytz
from django.conf import settings
from datetime import datetime, timedelta
from rest_framework import serializers
from rest_framework_mongoengine import serializers as mongoserializers

from .models import *
from core.models import Place


class ReservationSerializer(mongoserializers.DocumentSerializer):
    def select_table(self, place, date_time, guests, avg_time_spent):
        table_options = [size for size in range(guests, guests + 4) if size <= 10]
        min_border = date_time - timedelta(hours=avg_time_spent)
        max_border = date_time + timedelta(hours=avg_time_spent)
        conf = place.configuration.tables
        reserved_tables = [0]*10
        pipeline = [
            { "$group": { "_id": "$table_size", "count": { "$sum": 1 }}}
        ]

        reservations = Reservation.objects(
            place=place,
            date_time__gt=min_border,
            date_time__lt=max_border,
            table_size__in=table_options
        ).aggregate(pipeline)

        for table in list(reservations):
            reserved_tables[table['_id']-1] = table['count']

        for option in table_options:
            if conf[option-1] - reserved_tables[option-1] > 0:
                return option

        return None

    def validate(self, data):
        date_time = data.get('date_time')
        guests=data.get('table_size')
        place = Place.objects.get(id=data.get('place').id)

        timezone = pytz.timezone(place.timezone)
        date_time = date_time.replace(tzinfo=pytz.utc).astimezone(tz=timezone)
        yyyy = date_time.year
        mm = date_time.month
        dd = date_time.day
        today = date_time.weekday()
        yesterday = today - 1

        today_min = place.opening_hours[today][0].replace(tzinfo=pytz.utc).astimezone(tz=timezone).replace(yyyy, mm, dd)
        today_max = place.opening_hours[today][1].replace(tzinfo=pytz.utc).astimezone(tz=timezone).replace(yyyy, mm, dd)
        yesterday_min = place.opening_hours[yesterday][0].replace(tzinfo=pytz.utc).astimezone(tz=timezone).replace(yyyy, mm, dd)
        yesterday_max = place.opening_hours[yesterday][1].replace(tzinfo=pytz.utc).astimezone(tz=timezone).replace(yyyy, mm, dd)
        
        date_time_is_valid = (
            date_time >= datetime.now(tz=timezone) and (
            (yesterday_min >= yesterday_max and date_time < yesterday_max) or
            (today_min >= today_max and date_time >= today_min) or
            (date_time >= today_min and date_time < today_max))
        )

        if not date_time_is_valid:
            raise serializers.ValidationError('This place does not work at the time')
        
        table_size = self.select_table(place=place, date_time=date_time, guests=guests, avg_time_spent=3)
        if not table_size:
            raise serializers.ValidationError(f'At {date_time.strftime("%H:%M")} there are no vacant tables for {guests} people')

        data['table_size'] = table_size
        return data

    def create(self, validated_data):
        reservation = Reservation(**validated_data)
        reservation.save()
        return reservation

    def update(self, instance, validated_data):
        instance.update(**validated_data)
        return instance.reload()

    class Meta:
        model = Reservation
        fields = '__all__'