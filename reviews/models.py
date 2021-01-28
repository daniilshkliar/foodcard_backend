import mongoengine_goodjson as gj
from mongoengine import Document, fields

from backend.sources import noise


class GeneralReview(gj.Document):
    rating = fields.DecimalField(min_value=0, max_value=5, precision=1)
    rounded_rating = fields.IntField(min_value=0, max_value=5)
    food = fields.DecimalField(min_value=0, max_value=5, precision=1)
    service = fields.DecimalField(min_value=0, max_value=5, precision=1)
    ambience = fields.DecimalField(min_value=0, max_value=5, precision=1)
    noise = fields.StringField(max_length=10, choices=noise)
    amount = fields.IntField(min_value=0, default=0)
    distribution = fields.ListField(field=fields.IntField(min_value=0), max_length=5, default=[0]*5)