import base64
from hashlib import sha256
import hashlib
import hmac
import json
import random
from django.shortcuts import render, get_object_or_404
from django.views import View
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect, Http404, HttpResponseForbidden, StreamingHttpResponse
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from gallery.serializer import CustomerSerializer, ModelSerializer, OrderSerializer
from manager_resources import settings
from .models import Customer, Order, Gallery, Content, Model
from rest_framework.views import APIView 
from rest_framework.response import Response
from rest_framework import status
import jwt 
import requests
from jwt import ExpiredSignatureError, InvalidTokenError
import time


# Create your views here.
'''
def test_token(request):

    payload = {
        'iat': int(time.time()), 
        'exp': int(time.time() + 40),
        'user_id': 9
    }

    encode_jwt = jwt.encode(payload, '123', algorithm='HS256')

    return render(request, 'gallery/test_token.html', {
        'token': encode_jwt
    })
'''


class PageAuthenticate(View):
    def validate_token(self, token):
        secret_aunthenticate = settings.SECRET_AUTHENTIFICATE
        try:
            payload = jwt.decode(token, secret_aunthenticate, algorithms=['HS256'], 
                                 options={'verify_signature': True, 'require': ['exp']})
            return payload['user_id']
        except (ExpiredSignatureError, InvalidTokenError):
            return False
    

    def validate_user_orders(self, user_id):
        response = {'response': {'content': '', 'status': False}}
        try:
            find_user = Customer.objects.get(id=user_id, is_active=True)
        except ObjectDoesNotExist:
            response['response']['content'] = 'El usuario no existe o esta bloqueado'
            return response
        try:
            find_orders = find_user.user_gallery.orders
            if find_orders.exists():
                response['response']['content'] = find_user
                response['response']['status'] = True
            else:
                response['response']['content'] = 'El usuario no tiene ordenes activas pagadas'
        except: 
            response['response']['content'] = 'El usuario no tiene ordenes creadas'
        return response 
     

    def get(self, request, token):
        customer_find = self.validate_token(token)
        if not customer_find:
            return HttpResponseRedirect(reverse('index'))
        customer_order_find = self.validate_user_orders(customer_find)
        if not customer_order_find['response']['status']:
            return render(request,'404.html', {'message_error': customer_order_find['response']['content']}, status=404)
        user = customer_order_find['response']['content']
        login(request, user)
        return HttpResponseRedirect(reverse('index-gallery'))
        
@login_required
def LogoutUser(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))


def Index(request):
    return HttpResponseRedirect('https://myarea51.net/')


class IndexGallery(LoginRequiredMixin, View):
    def render_view(self, request, context):
        return render(request, 'gallery/index_gallery.html', context)


    def get(self, request):
        context={
            'username': request.user.email
        }
        return self.render_view(request, context)

    def post(self, request):
        content_type = request.POST['button_value']
        contents = Content.objects.filter(order__gallery__customer=request.user, 
                                          type=content_type, status=True).exclude(order__status='refunded').order_by('-date')
        context={
                'username': request.user.email,
                'contents': contents, 
                'content_type': content_type}
        
        return self.render_view(request, context)
        


class VideoPlayer(LoginRequiredMixin, View):
    
    tokens = []
    
    @classmethod
    def create_token(cls):
        token_create = random.randint(1000, 10000)
        cls.tokens.append(token_create)
        return token_create


    @classmethod
    def validate_token(cls, token):
        for takenKey in cls.tokens:
            if takenKey == token:
                cls.tokens.remove(takenKey)
                return True
        return False
            

    def get(self, request, pk):
        video_request = get_object_or_404(Content, id=pk)
        token = self.create_token()
        context = {
            'video_request': video_request,
            'token': token
        }
        return render(request, 'gallery/video_gallery.html', context)
        



@login_required
def StreamVideo(request, pk, token):
    video_player = get_object_or_404(Content, id=pk)
    url = video_player.url
    response = requests.get(url, stream=True)
    if VideoPlayer.validate_token(token): 
        return StreamingHttpResponse(
            streaming_content=response.iter_content(chunk_size=1048576),
            content_type = response.headers['Content-Type'],
            headers={
                'Content-Disposition': 'inline', 
                'X-Content-Type-Options': 'nosniff',  
            })
    else:
        return Http404()
    


def validate_webhook(request):
    secret_key = settings.WEBHOOK_KEY
    webhook_key = request.headers.get("X-WC-Webhook-Signature", "")
    webhook_key_bytes = base64.b64decode(webhook_key)
    webhook_key_hex = webhook_key_bytes.hex()

    generate_signature = hmac.new(
        secret_key.encode('utf-8'),
        request.body,
        digestmod=hashlib.sha256
    ).hexdigest()


    if hmac.compare_digest(webhook_key_hex, generate_signature):
        return True
    return False



class CustomerApiView(APIView):
    allowed_methods = ['POST']
    def post(self, request):
        if not validate_webhook(request):
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        try: 
            customerRegister = Customer.objects.get(id=request.data.get('id'))
            serializer = CustomerSerializer(customerRegister, data=request.data)
        except ObjectDoesNotExist: 
            serializer = CustomerSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)
      
    

class ModelApiView(APIView):
    allowed_methods = ['POST']
    def post(self, request):
        if not validate_webhook(request):
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        body = request.body.decode('utf-8')
        data = json.loads(body)
        data['image'] = data.get('images')[0]['src'] #imagen principal de la modelo
        try: 
            modelRegister = Model.objects.get(id=request.data.get('id'))
            serializer = ModelSerializer(modelRegister, data=data)
        except ObjectDoesNotExist: 
            serializer = ModelSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class OrderApiView(APIView):
    allowed_methods = ['POST']
    def post(self, request):
        allowed_status_post = [status.value for status in Order.TypesContent]
        if not validate_webhook(request):
            return Response(status=status.HTTP_401_UNAUTHORIZED)
      
        if request.data.get('status') not in allowed_status_post:
            return Response(status=status.HTTP_202_ACCEPTED)
    
        
        try:
            orderRegister = Order.objects.get(id=request.data.get('id'))
            serializer = OrderSerializer(orderRegister, data=request.data)
        except ObjectDoesNotExist:
            serializer = OrderSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(status=status.HTTP_200_OK)




        