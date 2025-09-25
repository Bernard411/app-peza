from django.shortcuts import render

# Create your views here.
def home(request):
    return render(request, 'index.html')

def login_view(request):
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