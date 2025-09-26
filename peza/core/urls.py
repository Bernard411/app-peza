from django.urls import path
from . import views
from . import peza_api
from django.views.generic import TemplateView
from django.urls import path
from .views import EmergencyContactListCreateView
from django.urls import path
from .views import InboxView, DMView, NotificationDetailView
from django.urls import path
from django.urls import path
from .views import InboxView, DMView, NotificationDetailView, ComposeView, MessageListCreateView, TypingStatusView
from django.urls import path
from .views import InboxView, DMView, NotificationDetailView, ComposeView, MessageListCreateView, TypingStatusView, DeleteMessageView, ClearChatView

from .views import ProfileView, UpdateNameView, ChangePasswordView, DeleteAccountView, ToggleNotificationsView, ToggleLocationView

from .views import InboxView, DMView, NotificationDetailView, ComposeView

urlpatterns = [
    
    path('home/', views.home, name='home'),
    path('', views.login_view, name='login'),
    path('register/', views.register, name='register'),
    path('alert/', views.alert, name='alert'),

    path('pachineba/', views.pachineba, name='pachineba'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('settings/', views.settings, name='settings'),
    path('services/', views.services, name='services'),
    # path('inbox/', views.inbox, name='inbox'),
    path('near_by_places/', views.near_by_places, name='near_by_places'),
    path('pay/', views.pay, name='pay'),
    path('maps/', views.maps, name='maps'),
    path('emergency_contact/', views.emergency_contact, name='emergency_contact'),
    path('logout/', views.logout_view, name='logout'),
    path('signup/', views.signup, name='signup'),
    path('api/peza/', peza_api.peza_api, name='peza_api'),

    path('map/', TemplateView.as_view(template_name='maps.html'), name='map'),

    path('api/emergency-contacts/', EmergencyContactListCreateView.as_view(), name='emergency_contacts_list_create'),




    path('inbox/', InboxView.as_view(), name='inbox'),
    path('dm/<int:user_id>/', DMView.as_view(), name='dm'),
    path('notification/<int:pk>/', NotificationDetailView.as_view(), name='notification_detail'),
    path('compose/', ComposeView.as_view(), name='compose'),
    path('api/messages/<int:user_id>/', MessageListCreateView.as_view(), name='message_list_create'),
    path('api/typing/<int:user_id>/', TypingStatusView.as_view(), name='typing_status'),
    path('api/delete-message/<int:message_id>/', DeleteMessageView.as_view(), name='delete_message'),
    path('api/clear-chat/<int:user_id>/', ClearChatView.as_view(), name='clear_chat'),



    path('profile/', ProfileView.as_view(), name='profile'),
    path('api/update-name/', UpdateNameView.as_view(), name='update_name'),
    path('api/change-password/', ChangePasswordView.as_view(), name='change_password'),
    path('api/delete-account/', DeleteAccountView.as_view(), name='delete_account'),
    path('api/toggle-notifications/', ToggleNotificationsView.as_view(), name='toggle_notifications'),
    path('api/toggle-location/', ToggleLocationView.as_view(), name='toggle_location'),
]