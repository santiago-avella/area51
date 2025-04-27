from django.contrib import admin
from .models import *

# Register your models here.


class AdminModel(admin.ModelAdmin):
    list_display = ['id', 'name', 'status']
    list_filter = ['status']


class AdmimContent(admin.ModelAdmin):
    list_display = ['type', 'description', 'status', 'date']
    list_filter = ['type', 'status', 'date', 'order', 'model']


class AdminCustomer(admin.ModelAdmin):
    list_display = ['id', 'username', 'is_active']
    list_filter = ['is_active']


class AdminOrder(admin.ModelAdmin):
    list_display = ['id', 'date_created', 'status', 'gallery']
    list_filter = ['date_created', 'status', 'gallery']



class AdminGallery(admin.ModelAdmin):
    list_display = ['customer_id', 'status']
    list_filter = ['status']
    


admin.site.register(Model, AdminModel)
admin.site.register(Content, AdmimContent)
admin.site.register(Customer, AdminCustomer)
admin.site.register(Order, AdminOrder)
admin.site.register(Gallery, AdminGallery)