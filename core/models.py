from djongo import models


class Category(models.Model):
    _id = models.ObjectIdField()
    title = models.CharField(max_length=20, unique=True)
    

class Cuisine(models.Model):
    _id = models.ObjectIdField()
    title = models.CharField(max_length=30, unique=True)
    

class AdditionalService(models.Model):
    _id = models.ObjectIdField()
    title = models.CharField(max_length=50, unique=True)


class Address(models.Model):
    country = models.CharField(max_length=30)
    city = models.CharField(max_length=30)
    street = models.CharField(max_length=70)
    # coordinates = models.ArrayField(models.DecimalField())
    
    class Meta:
        abstract = True


class GeneralReview(models.Model):
    rating = models.DecimalField(max_digits=2, decimal_places=1)
    food = models.DecimalField(max_digits=2, decimal_places=1)
    service = models.DecimalField(max_digits=2, decimal_places=1)
    ambience = models.DecimalField(max_digits=2, decimal_places=1)
    noise = models.CharField(max_length=10)
    amount = models.IntegerField()
    # distribution = models.ArrayField(models.IntegerField())

    class Meta:
        abstract = True


class Place(models.Model):
    _id = models.ObjectIdField()
    title = models.CharField(max_length=70)
    categories = models.ArrayReferenceField(to=Category, on_delete=models.CASCADE)
    cuisines = models.ArrayReferenceField(to=Cuisine, on_delete=models.CASCADE)
    additional = models.ArrayReferenceField(to=AdditionalService, on_delete=models.CASCADE)
    description = models.TextField()
    phone = models.CharField(max_length=20)
    instagram = models.URLField()
    website = models.URLField()
    rounded_rating = models.IntegerField()
    general_review = models.EmbeddedField(model_container=GeneralReview)
    address = models.EmbeddedField(model_container=Address)
    # operation_hours = models.ArrayField(models.TimeField())
    # photos = models.ArrayField(models.ImageField(upload_to='photo'))
    
    objects = models.DjongoManager()
	# table2 = models.IntegerField()