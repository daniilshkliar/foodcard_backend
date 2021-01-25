import mongoengine_goodjson as gj
from datetime import datetime
from mongoengine import Document, EmbeddedDocument, fields, PULL, CASCADE, NULLIFY
import backend.sources as src


class Address(gj.EmbeddedDocument):
    country = fields.StringField(required=True, max_length=50)
    city = fields.StringField(required=True, max_length=50)
    street = fields.StringField(required=True, max_length=70)
    coordinates = fields.GeoPointField(required=True)


class GeneralReview(gj.Document):
    rating = fields.DecimalField(min_value=0, max_value=5, precision=1)
    rounded_rating = fields.IntField(min_value=0, max_value=5)
    food = fields.DecimalField(min_value=0, max_value=5, precision=1)
    service = fields.DecimalField(min_value=0, max_value=5, precision=1)
    ambience = fields.DecimalField(min_value=0, max_value=5, precision=1)
    noise = fields.StringField(max_length=10, choices=src.noise)
    amount = fields.IntField(min_value=0, default=0)
    distribution = fields.ListField(field=fields.IntField(min_value=0, default=0), max_length=5, default=[])


class Place(gj.Document):
    title = fields.StringField(required=True, max_length=70, unique_with='address')
    main_category = fields.StringField(max_length=30, choices=src.categories)
    categories = fields.ListField(fields.StringField(max_length=30, choices=src.categories), default=[])
    main_cuisine = fields.StringField(max_length=30, choices=src.cuisines)
    cuisines = fields.ListField(fields.StringField(max_length=30, choices=src.cuisines), default=[])
    additional_services = fields.ListField(fields.StringField(max_length=30, choices=src.additional_services), default=[])
    description = fields.StringField(max_length=3000)
    phone = fields.StringField(required=True, max_length=20, unique=True)
    instagram = fields.URLField()
    website = fields.URLField()
    operation_hours = fields.ListField(field=fields.ListField(field=fields.DateTimeField(default=datetime.utcnow), max_length=2), max_length=7)
    general_review = fields.ReferenceField(GeneralReview, reverse_delete_rule=NULLIFY, unique=True)
    address = fields.EmbeddedDocumentField(Address, required=True)
    main_photo = fields.StringField()
    photos = fields.ListField(fields.StringField(), default=[])
    is_active = fields.BooleanField(default=False)
	# table2 = models.IntegerField()


class Favorite(gj.Document):
    user = fields.IntField(min_value=0, required=True, unique=True)
    places = fields.ListField(field=fields.ReferenceField(Place, reverse_delete_rule=PULL), default=[])