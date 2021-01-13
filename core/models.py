import mongoengine_goodjson as gj
from datetime import datetime
from mongoengine import Document, EmbeddedDocument, fields, PULL, CASCADE, DENY, errors


class City(gj.Document):
    city = fields.StringField(required=True, max_length=70)


class Country(gj.Document):
    country = fields.StringField(required=True, max_length=70, unique=True)
    cities = fields.ListField(field=fields.ReferenceField(City, reverse_delete_rule=PULL), default=[])


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
    country = fields.ReferenceField(Country)
    city = fields.ReferenceField(City)
    street = fields.StringField(max_length=50)
    coordinates = fields.EmbeddedDocumentField(Coordinates)


class GeneralReview(gj.Document):
    rating = fields.DecimalField(min_value=0, max_value=5, precision=1, default=None)
    food = fields.DecimalField(min_value=0, max_value=5, precision=1, default=None)
    service = fields.DecimalField(min_value=0, max_value=5, precision=1, default=None)
    ambience = fields.DecimalField(min_value=0, max_value=5, precision=1, default=None)
    noise = fields.StringField(max_length=10)
    amount = fields.IntField(min_value=0, default=0)
    distribution = fields.ListField(field=fields.IntField(default=0, min_value=0), max_length=5, default=[])


class Place(gj.Document):
    title = fields.StringField(required=True, max_length=70)
    categories = fields.ListField(fields.ReferenceField(Category, reverse_delete_rule=PULL), default=[])
    cuisines = fields.ListField(fields.ReferenceField(Cuisine, reverse_delete_rule=PULL), default=[])
    additional_services = fields.ListField(fields.ReferenceField(AdditionalService, reverse_delete_rule=PULL), default=[])
    description = fields.StringField(max_length=3000)
    phone = fields.StringField(required=True, max_length=15, unique=True)
    instagram = fields.URLField()
    website = fields.URLField()
    rounded_rating = fields.IntField(min_value=0, max_value=5)
    operation_hours = fields.ListField(field=fields.ListField(field=fields.DateTimeField(default=datetime.utcnow), max_length=2), max_length=7)
    general_review = fields.ReferenceField(GeneralReview, reverse_delete_rule=DENY, unique=True)
    address = fields.EmbeddedDocumentField(Address)
    photos = fields.ListField(fields.StringField(), default=[])
	# table2 = models.IntegerField()


class Favorite(gj.Document):
    user = fields.IntField(min_value=0, required=True, unique=True)
    places = fields.ListField(field=fields.ReferenceField(Place, reverse_delete_rule=PULL), default=[])