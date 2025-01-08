from django.shortcuts import redirect, render
from django.contrib.auth import get_user_model, login, logout, authenticate
# Create your views here.

User = get_user_model() ## faire f12 sur get_user_model pour voir la source


def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = User.objects.create_user(username=username,
                                        password=password)
        login(request, user)
        return redirect('index')
    return render(request, 'account/signup.html')

def login_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            return redirect('index')
        # ou
        # user = User.objects.get(username=username)
        # if user.check_password(password):
        #     login(request, user)
        #     return redirect('index')
    return render(request, 'account/login.html')

def logout_user(request):
    logout(request)
    return redirect('index')
