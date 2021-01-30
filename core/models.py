import mongoengine_goodjson as gj
from datetime import datetime
from mongoengine import Document, EmbeddedDocument, fields, PULL, NULLIFY

import backend.sources as src
from reviews.models import GeneralReview


class Address(gj.EmbeddedDocument):
    country = fields.StringField(required=True, max_length=50)
    city = fields.StringField(required=True, max_length=50)
    street = fields.StringField(required=True, max_length=70)
    coordinates = fields.GeoPointField(required=True)


class Image(gj.Document):
    image_name = fields.StringField()
    image_uri = fields.URLField()
    thumbnail_name = fields.StringField()
    thumbnail_uri = fields.URLField()


class Configuration(gj.EmbeddedDocument):
    tables = fields.ListField(fields.IntField(min_value=0), max_length=10, default=[0]*10)


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
    timezone = fields.StringField(required=True)
    opening_hours = fields.ListField(field=fields.ListField(field=fields.DateTimeField(default=datetime.utcnow), max_length=2), max_length=7, default=[[None,None]]*7)
    address = fields.EmbeddedDocumentField(Address, required=True)
    main_photo = fields.ReferenceField(Image, reverse_delete_rule=NULLIFY)
    photos = fields.ListField(fields.ReferenceField(Image, reverse_delete_rule=PULL), default=[])
    general_review = fields.ReferenceField(GeneralReview, reverse_delete_rule=NULLIFY, unique=True)
    configuration = fields.EmbeddedDocumentField(Configuration)
    is_active = fields.BooleanField(default=False)


class Favorite(gj.Document):
    user = fields.IntField(min_value=0, required=True, unique=True)
    places = fields.ListField(field=fields.ReferenceField(Place, reverse_delete_rule=PULL), default=[])