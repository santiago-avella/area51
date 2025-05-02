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
            model = Model.objects.get(id=value)
            return model
        except:
            raise serializers.ValidationError('Modelo no encontrada')

    def validate_meta_data(self, value):
        required_fields = {'que-cantidad-o-duracion': 'variation', 'que-contenido-quieres': 'type_content', '¿Cómo lo quieres?': 'description'}
        format_content = {'Video': 'vid', 'Audio': 'aud', 'Fotografía': 'img'}
        info_variation = {}
        for item in value:
            if item['key'] not in required_fields.keys():
                raise serializers.ValidationError('Faltan campos requeridos')
            info_variation[required_fields[item['key']]] = item['value']
        info_variation['variation'] = info_variation['variation'].replace('x', '') # el formato es x10, x5, x1 para cantidades, se desprecia el 1er caracter
        if info_variation['type_content'] not in format_content.keys():
            raise serializers.ValidationError('Hay valores no permitidos')
        info_variation['type_content'] = format_content[info_variation['type_content']]
        return info_variation


class OrderSerializer(serializers.ModelSerializer):
    gallery = serializers.IntegerField(read_only=True)
    customer_id = serializers.IntegerField(write_only=True)
    line_items = ContentSerializer(many=True)

    class Meta: 
        model = Order
        fields = ['id', 'status', 'date_created', 'gallery', 'customer_id', 'line_items']


    def create_content(self, item, order):
        try:
            Content.objects.create(type=item['meta_data']['type_content'], 
                                   variation=item['meta_data']['variation'],
                                   description=item['meta_data']['description'],
                                   model=item['product_id'], order=order)
        except:
            print('error')
            raise serializers.ValidationError('No se pudo guardar la informacion de itmes por orden')


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
            if item['meta_data']['type_content'] == 'img':
                for i in range(1, int(item['meta_data']['variation'])):
                    self.create_content(item, order)
            self.create_content(item, order)
        return order


