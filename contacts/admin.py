from django.contrib import admin

# Register your models here.
#admin, pass lam12345.,email: admin@cm.com
from .models import Category
admin.site.register(Category)