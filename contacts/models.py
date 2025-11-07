from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Category(models.Model):
    title = models.CharField(max_length=225)

class Contact(models.Model):
    catagory = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='contacts')
    first_name = models.CharField(max_length=225)
    last_name = models.CharField(max_length=225)
    phone_number = models.CharField(max_length=25, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(max_length=255)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_contacts', null=True, blank=True)
    shared_with = models.ManyToManyField(User, related_name='shared_contacts', blank=True)


class ContactEmail(models.Model):
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE, related_name='emails')
    email = models.EmailField()


class ContactPhone(models.Model):
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE, related_name='phones')
    phone_number = models.CharField(max_length=25)
