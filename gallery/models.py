from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class Customer(AbstractUser):
    username = models.CharField(unique=True, max_length=150,blank=True, null=True, default=None)
    password = models.CharField(max_length=128, blank=True, null=True)
    
    def __str__(self):
        return f'{self.id} - {self.username}'

class Gallery(models.Model):
    status = models.BooleanField(default=True)
    customer = models.OneToOneField(Customer, on_delete=models.PROTECT, related_name='user_gallery')

    def __str__(self):
        return str(self.customer)

class Order(models.Model):
    class TypesContent(models.TextChoices):
        COMPLETED = 'completed', 'Completada'
        PROCESSING = 'processing', 'Procesando'
        REFUNDED = 'refunded', 'Reembolsada'
    id = models.IntegerField(primary_key=True)
    date_created = models.DateTimeField()
    status = models.CharField(max_length=30, choices=TypesContent.choices)
    gallery = models.ForeignKey(Gallery, on_delete=models.PROTECT, related_name='orders')
    
    def __str__(self):
        return f'orden: <{self.id}> / cliente: <{self.gallery}>'



class Model(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=50)
    status = models.CharField(max_length=20)
    image = models.CharField(max_length=200, blank=True, null=True) 

    def __str__(self):
        return f'{self.id} - {self.name}'

class Content(models.Model):
    class TypesContent(models.TextChoices):
        VIDEO = 'vid', 'Video' 
        AUDIO = 'aud', 'Audio'
        IMAGE = 'img', 'Imagen'
    type = models.CharField(max_length=10, choices=TypesContent.choices)
    description = models.TextField(max_length=200, blank=True)
    status = models.BooleanField(default=False)
    variation = models.CharField(max_length=3, blank=True)
    url = models.CharField(max_length=150, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    miniature = models.CharField(max_length=150, blank=True)
    order = models.ForeignKey(Order, on_delete=models.PROTECT, related_name='contents')
    model = models.ForeignKey(Model, on_delete=models.PROTECT, related_name='contents_model')



class test(models.Model):
    id = models.IntegerField(primary_key=True)