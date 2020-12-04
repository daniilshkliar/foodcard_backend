import mongoengine_goodjson as gj
from datetime import datetime
from mongoengine import Document, EmbeddedDocument, fields, PULL, CASCADE


class Category(gj.Document):
    title = fields.StringField(required=True, max_length=50, unique=True)


class Cuisine(gj.Document):
    title = fields.StringField(required=True, max_length=50, unique=True)


class AdditionalService(gj.Document):
    title = fields.StringField(required=True, max_length=50, unique=True)


class Coordinates(gj.EmbeddedDocument):
    latitude = fields.DecimalField(min_value=-90, max_value=90, precision=7)
    longitude = fields.DecimalField(min_value=-180, max_value=180, precision=7)


class Address(gj.EmbeddedDocument):
    country = fields.StringField(required=True, max_length=50)
    city = fields.StringField(required=True, max_length=50)
    street = fields.StringField(required=True, max_length=50)
    coordinates = fields.EmbeddedDocumentField(Coordinates)


class GeneralReview(gj.EmbeddedDocument):
    rating = fields.DecimalField(min_value=0, max_value=5, precision=1)
    food = fields.DecimalField(min_value=0, max_value=5, precision=1)
    service = fields.DecimalField(min_value=0, max_value=5, precision=1)
    ambience = fields.DecimalField(min_value=0, max_value=5, precision=1)
    noise = fields.StringField(max_length=10)
    amount = fields.IntField(default=0, min_value=0)
    distribution = fields.ListField(field=fields.IntField(default=0, min_value=0), max_length=5, default=None)


class Place(gj.Document):
    title = fields.StringField(required=True, max_length=70)
    categories = fields.ListField(fields.ReferenceField(Category, reverse_delete_rule=PULL), required=True, default=None)
    cuisines = fields.ListField(fields.ReferenceField(Cuisine, reverse_delete_rule=PULL), default=None)
    additional = fields.ListField(fields.ReferenceField(AdditionalService, reverse_delete_rule=PULL), default=None)
    description = fields.StringField(required=True)
    phone = fields.StringField(required=True, max_length=20)
    instagram = fields.URLField()
    website = fields.URLField()
    rounded_rating = fields.IntField(min_value=0, max_value=5)
    operation_hours = fields.ListField(field=fields.ListField(field=fields.DateTimeField(default=datetime.utcnow), max_length=2), max_length=7, default=None)
    general_review = fields.EmbeddedDocumentField(GeneralReview)
    address = fields.EmbeddedDocumentField(Address)
    photos = fields.ListField(fields.ImageField(collection_name='photo'), default=None)
	# table2 = models.IntegerField()


class Favorite(gj.Document):
    user_id = fields.IntField(min_value=0, required=True)
    place = fields.ReferenceField(Place, reverse_delete_rule=CASCADE, required=True)