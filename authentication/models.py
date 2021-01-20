import mongoengine_goodjson as gj
from mongoengine import Document, fields, PULL

from core.models import Place


class Manager(gj.Document):
    user = fields.IntField(min_value=0, required=True, unique=True)
    places = fields.ListField(field=fields.ReferenceField(Place, reverse_delete_rule=PULL), default=[])