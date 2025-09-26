from django.shortcuts import render, redirect
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.models import User

# Create your views here.
def home(request):
    return render(request, 'index.html')

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'login.html', {'error': 'Invalid email or password.'})
    return render(request, 'login.html')


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import EmergencyContact
from .serializers import EmergencyContactSerializer
from rest_framework.permissions import IsAuthenticated

class EmergencyContactListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        contacts = EmergencyContact.objects.filter(user=request.user)
        serializer = EmergencyContactSerializer(contacts, many=True)
        return Response(serializer.data)

    def post(self, request):
        contacts_data = request.data
        if not isinstance(contacts_data, list):
            contacts_data = [contacts_data]
        
        responses = []
        for contact_data in contacts_data:
            contact_data['user'] = request.user.id
            serializer = EmergencyContactSerializer(data=contact_data)
            if serializer.is_valid():
                serializer.save()
                responses.append(serializer.data)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(responses, status=status.HTTP_201_CREATED)
    


from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView, DetailView
from django.db.models import Q, Value
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Message, Notification, User, TypingStatus, Profile
from .serializers import MessageSerializer
from django.utils import timezone

class InboxView(LoginRequiredMixin, TemplateView):
    template_name = 'inbox.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        notifs = list(Notification.objects.filter(user=user).values('id', 'title', 'content', 'timestamp', 'is_read', 'type').annotate(item_type=Value('notification')))

        messages = Message.objects.filter(Q(sender=user) | Q(recipient=user)).order_by('-timestamp')
        conversations = {}
        for msg in messages:
            corr = msg.recipient if msg.sender == user else msg.sender
            if corr not in conversations:
                conversations[corr] = {
                    'correspondent': corr,
                    'latest_message': msg,
                    'unread_count': 0 if msg.is_read or msg.sender == user else 1
                }
            else:
                if msg.timestamp > conversations[corr]['latest_message'].timestamp:
                    conversations[corr]['latest_message'] = msg
                if not msg.is_read and msg.recipient == user:
                    conversations[corr]['unread_count'] += 1

        convs = []
        for corr, data in conversations.items():
            convs.append({
                'id': corr.id,
                'correspondent': data['correspondent'],
                'content': data['latest_message'].content,
                'timestamp': data['latest_message'].timestamp,
                'unread_count': data['unread_count'],
                'item_type': 'conversation'
            })

        all_items = notifs + convs
        all_items.sort(key=lambda x: x['timestamp'], reverse=True)

        context['inbox_items'] = all_items
        return context

class DMView(LoginRequiredMixin, TemplateView):
    template_name = 'dm.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        other_user_id = self.kwargs['user_id']
        other_user = get_object_or_404(User, id=other_user_id)
        
        messages = Message.objects.filter(
            (Q(sender=user, recipient=other_user) | Q(sender=other_user, recipient=user))
        ).order_by('timestamp')

        messages.filter(recipient=user, is_read=False).update(is_read=True)

        context['other_user'] = other_user
        context['messages'] = messages
        context['last_message_id'] = messages.last().id if messages.exists() else 0
        return context

class NotificationDetailView(LoginRequiredMixin, DetailView):
    model = Notification
    template_name = 'notification_detail.html'
    context_object_name = 'notification'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.user != self.request.user:
            raise Http404
        if not obj.is_read:
            obj.is_read = True
            obj.save()
        return obj

class ComposeView(LoginRequiredMixin, TemplateView):
    template_name = 'compose.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        users = User.objects.exclude(id=user.id).select_related('profile')
        context['users'] = users
        return context

class MessageListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        other_user = get_object_or_404(User, id=user_id)
        last_id = request.GET.get('last_id', 0)
        messages = Message.objects.filter(
            (Q(sender=request.user, recipient=other_user) | Q(sender=other_user, recipient=request.user)),
            id__gt=last_id
        ).order_by('timestamp')
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)

    def post(self, request, user_id):
        other_user = get_object_or_404(User, id=user_id)
        data = request.data
        data['sender'] = request.user.id
        data['recipient'] = other_user.id
        serializer = MessageSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DeleteMessageView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, message_id):
        message = get_object_or_404(Message, id=message_id)
        if message.sender != request.user and message.recipient != request.user:
            return Response({'error': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)
        message.delete()
        return Response({'status': 'deleted'}, status=status.HTTP_200_OK)

class ClearChatView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, user_id):
        other_user = get_object_or_404(User, id=user_id)
        Message.objects.filter(
            (Q(sender=request.user, recipient=other_user) | Q(sender=other_user, recipient=request.user))
        ).delete()
        return Response({'status': 'chat cleared'}, status=status.HTTP_200_OK)

class TypingStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, user_id):
        recipient = get_object_or_404(User, id=user_id)
        is_typing = request.data.get('is_typing', False)
        TypingStatus.objects.update_or_create(
            user=request.user,
            recipient=recipient,
            defaults={'is_typing': is_typing}
        )
        TypingStatus.cleanup_old()
        return Response({'status': 'updated'}, status=status.HTTP_200_OK)

    def get(self, request, user_id):
        recipient = get_object_or_404(User, id=user_id)
        try:
            status = TypingStatus.objects.get(user=recipient, recipient=request.user)
            TypingStatus.cleanup_old()
            return Response({'is_typing': status.is_typing})
        except TypingStatus.DoesNotExist:
            return Response({'is_typing': False})

def register(request):
    return render(request, 'register.html')

def alert(request):
    return render(request, 'alert.html')

from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import logout
from .models import Profile, EmergencyContact

class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        try:
            profile = user.profile
        except Profile.DoesNotExist:
            # Create profile if it doesn't exist
            profile = Profile.objects.create(user=user)
        context['user'] = user
        context['profile'] = profile
        context['emergency_contacts'] = EmergencyContact.objects.filter(user=user)
        return context

# ... (rest of the views as previously provided)


class UpdateNameView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')
        if first_name and last_name:
            user.first_name = first_name
            user.last_name = last_name
            user.save()
            return Response({'status': 'success', 'message': 'Name updated successfully'})
        return Response({'error': 'Invalid data'}, status=status.HTTP_400_BAD_REQUEST)

class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        if user.check_password(old_password):
            user.set_password(new_password)
            user.save()
            return Response({'status': 'success', 'message': 'Password changed successfully'})
        return Response({'error': 'Invalid old password'}, status=status.HTTP_400_BAD_REQUEST)

class DeleteAccountView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        user = request.user
        logout(request)  # Log out before deleting
        user.delete()
        return Response({'status': 'success', 'message': 'Account deleted successfully'})

class ToggleNotificationsView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        profile = request.user.profile
        profile.notifications_enabled = not profile.notifications_enabled
        profile.save()
        return Response({'status': 'success', 'enabled': profile.notifications_enabled})

class ToggleLocationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        profile = request.user.profile
        profile.location_sharing = not profile.location_sharing
        profile.save()
        return Response({'status': 'success', 'enabled': profile.location_sharing})

def pachineba(request):
    return render(request, 'pachineba.html')

def dashboard(request):
    return render(request, 'dashboard.html')


def settings(request):
    return render(request, 'settings.html')

def services(request):
    return render(request, 'services.html')

def inbox(request):
    return render(request, 'inbox.html')

def near_by_places(request):
    return render(request, 'near_by_places.html')   

def pay(request):
    return render(request, 'pay.html')

def maps(request):
    return render(request, 'maps.html')


def emergency_contact(request):
    return render(request, 'contacts.html')


def logout_view(request):
    logout(request)
    return redirect('login')

from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.core.exceptions import ValidationError
from .models import Profile

def signup(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        avatar = request.FILES.get('avatar')  # Handle file upload

        # Validation
        if not full_name or len(full_name.strip()) < 2:
            return render(request, 'signup.html', {'error': 'Please enter a valid full name (at least 2 characters).'})

        if not email or '@' not in email or '.' not in email:
            return render(request, 'signup.html', {'error': 'Please enter a valid email.'})

        if not password or len(password) < 6:
            return render(request, 'signup.html', {'error': 'Password must be at least 6 characters.'})

        if password != confirm_password:
            return render(request, 'signup.html', {'error': 'Passwords do not match.'})

        if User.objects.filter(username=email).exists():
            return render(request, 'signup.html', {'error': 'Email is already registered.'})

        try:
            # Create user
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
                first_name=full_name.split()[0],
                last_name=' '.join(full_name.split()[1:]) if len(full_name.split()) > 1 else ''
            )
            # Explicitly create profile
            profile = Profile.objects.create(user=user)
            if avatar:
                profile.avatar = avatar
                profile.save()
            # Log the user in
            login(request, user)
            return redirect('profile')  # Redirect to profile page
        except ValidationError:
            return render(request, 'signup.html', {'error': 'Invalid input provided.'})
        except Exception as e:
            return render(request, 'signup.html', {'error': f'An error occurred: {str(e)}'})

    return render(request, 'signup.html')
