from django.shortcuts import redirect, render
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth import authenticate, login, logout

# Create your views here.
def register_view(request):
    if request.method == "POST":
        required_keys = ['username', 'password', 'confirm_password']
        for key in required_keys:
            # print(key, request.POST.get(key))
            if request.POST.get(key) is None:
                return render(request, 'users/register.html', {'error': f"'{key}' is required."})

        username = request.POST.get("username")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password != confirm_password:
            return render(request, 'users/register.html', {'error': "Password and Confirm Password should be same."})

        user_exists = User.objects.filter(username=username).exists()
        if user_exists:
            return render(request, 'users/register.html', {'error': "User already taken."})

        user = User(
            username=username,
            password=make_password(password)
        )
        user.save()
        return redirect('user:login')
    else:
        return render(request, 'users/register.html')
    

def login_view(request):
    if request.method == "POST":
        required_keys = ['username', 'password']
        for key in required_keys:
            # print(key, request.POST.get(key))
            if request.POST.get(key) is None:
                return render(request, 'users/login.html', {'error': f"'{key}' is required."})

        username = request.POST.get("username")
        password = request.POST.get("password")

        user_exist = User.objects.filter(username=username).exists()
        if not user_exist:
            return render(request, 'users/login.html', {'error': "User does not exist, please regsiter then attempt to login."})

        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("root")
        else:
           return render(request, 'users/login.html', {'error': "Incorrect Password."})
    else:
        return render(request, 'users/login.html')

def logout_view(request):
    logout(request)  # Default logout
    return redirect('root')