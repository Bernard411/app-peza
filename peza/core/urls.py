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
    
]