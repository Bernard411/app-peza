from django.urls import path
from . import views
from . import peza_api
from django.views.generic import TemplateView
urlpatterns = [
    
    path('home/', views.home, name='home'),
    path('', views.login_view, name='login'),
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
    path('maps/', views.maps, name='maps'),
    path('emergency_contact/', views.emergency_contact, name='emergency_contact'),
    path('logout/', views.logout_view, name='logout'),
    path('signup/', views.signup, name='signup'),
    path('api/peza/', peza_api.peza_api, name='peza_api'),

    path('map/', TemplateView.as_view(template_name='maps.html'), name='map'),
    # Ensure 'home' is defined, e.g.:
   
]