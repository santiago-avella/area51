from rest_framework import serializers
from django.shortcuts import get_object_or_404
from .models import *

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'username', 'email']
    


class ModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Model
        fields = ['id', 'name', 'status', 'image']



class ContentSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    meta_data = serializers.ListField(child=serializers.DictField())


    def validate_product_id(self, value):
        try: 
            modelo = Model.objects.get(id=value)
            return modelo
        except:
            raise serializers.ValidationError('Modelo no encontrada')

    def validate_meta_data(self, value):
        info_content = {'type_content': value[0]['value'], 'duration':value[1]['value'], 
                        'description': value[2]['value']} #valores del meta_data
        return info_content


class OrderSerializer(serializers.ModelSerializer):
    gallery = serializers.IntegerField(read_only=True)
    customer_id = serializers.IntegerField(write_only=True)
    line_items = ContentSerializer(many=True)

    class Meta: 
        model = Order
        fields = ['id', 'status', 'date_created', 'gallery', 'customer_id', 'line_items']

    def create(self, validated_data):
        items_order = validated_data.pop('line_items')
        customer_id = validated_data.pop('customer_id')
        customer = get_object_or_404(Customer, id=customer_id)
        try:
            gallery, gallery_create = Gallery.objects.get_or_create(customer=customer)
        except Gallery.DoesNotExist:
            raise serializers.ValidationError('La galeria no existe')

        order = Order.objects.create(gallery=gallery, **validated_data)

        for item in items_order:
            try:
                Content.objects.create(type=item['meta_data']['type_content'], 
                                   description=item['meta_data']['description'],
                                   model=item['product_id'], order=order)
            except:
                raise serializers.ValidationError('No se pudo guardar la informacion de itmes por orden')
        return order


