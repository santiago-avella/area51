from django.urls import path
from . import views

urlpatterns = [
    path('', views.Index, name='index'),
    path('authentificate/<str:token>/', views.PageAuthenticate.as_view(), name='auth'),
    path('logout/', views.LogoutUser, name='logout'),
    path('gallery/', views.IndexGallery.as_view(), name='index-gallery'),
    path('gallery/videos/<int:pk>/', views.VideoPlayer.as_view(), name='video-player'),
    path('gallery/videos/<int:pk>/<int:token>/', views.StreamVideo, name='stream-video'),
    path('api/customer/', views.CustomerApiView.as_view()),
    path('api/model/', views.ModelApiView.as_view()), 
    path('api/order/', views.OrderApiView.as_view())
]