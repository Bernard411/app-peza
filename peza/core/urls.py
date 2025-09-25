from django.urls import path
from . import views

urlpatterns = [
    
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register, name='register'),
    path('alert/', views.alert, name='alert'),
    path('profile/', views.profile, name='profile'),
    path('pachineba/', views.pachineba, name='pachineba'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('settings/', views.settings, name='settings'),
    path('services/', views.services, name='services'),
    path('inbox/', views.inbox, name='inbox'),
    path('near_by_places/', views.near_by_places, name='near_by_places'),
    path('pay/', views.pay, name='pay'),
    
]