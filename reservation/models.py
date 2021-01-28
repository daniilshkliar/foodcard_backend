import mongoengine_goodjson as gj
from mongoengine import Document, EmbeddedDocument, fields, CASCADE

from core.models import Place


class Reservation(gj.Document):
    place = fields.ReferenceField(Place, reverse_delete_rule=CASCADE, required=True)
    user = fields.IntField(min_value=0)
    first_name = fields.StringField(max_length=50, required=True)
    last_name = fields.StringField(max_length=50)
    email = fields.StringField(max_length=70)
    phone = fields.StringField(max_length=20, required=True)
    date_time = fields.DateTimeField(default=datetime.utcnow, required=True)
    table_size = fields.IntField(min_value=1, max_value=15, required=True)
    comment = fields.StringField(max_length=300)