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

def register(request):
    return render(request, 'register.html')

def alert(request):
    return render(request, 'alert.html')

def profile(request):
    return render(request, 'profile.html')

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

def signup(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # Validation
        if not full_name or len(full_name.strip()) < 2:
            return render(request, 'signup.html', {'error': 'Please enter a valid full name (at least 2 characters).'})

        if not email or not '@' in email or not '.' in email:
            return render(request, 'signup.html', {'error': 'Please enter a valid email.'})

        if not password or len(password) < 6:
            return render(request, 'signup.html', {'error': 'Password must be at least 6 characters.'})

        if password != confirm_password:
            return render(request, 'signup.html', {'error': 'Passwords do not match.'})

        # Check if email already exists
        if User.objects.filter(username=email).exists():
            return render(request, 'signup.html', {'error': 'Email is already registered.'})

        try:
            # Create user
            user = User.objects.create_user(
                username=email,  # Using email as username to match login_view
                email=email,
                password=password,
                first_name=full_name.split()[0],
                last_name=' '.join(full_name.split()[1:]) if len(full_name.split()) > 1 else ''
            )
            # Log the user in after signup
            login(request, user)
            return render(request, 'signup.html', {'success': True})
        except ValidationError:
            return render(request, 'signup.html', {'error': 'Invalid input provided.'})
        except Exception as e:
            return render(request, 'signup.html', {'error': 'An error occurred during registration. Please try again.'})

    return render(request, 'signup.html')