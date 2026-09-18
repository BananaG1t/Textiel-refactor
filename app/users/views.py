from django.http import HttpResponse
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.shortcuts import redirect, render
from .forms import ProfileForm

# Create your views here.
def view_users(request):
    return render(request, 'users.html')

def login(request):
    if request.method == 'POST':
        email = request.POST["email"]
        password = request.POST["password"]

        user = authenticate(
            request,
            username=email,
            password=password,
        )

        if user is not None:
            auth_login(request, user)
            return redirect("/")


    if request.method == 'GET':
        return render(request, 'login.html')

    return HttpResponse("Method not allowed", status=405)

def password_reset(request):
    if request.method == 'POST':
        # Handle password reset logic here
        pass

    if request.method == 'GET':
        return render(request, 'password_reset.html')

    return HttpResponse("Method not allowed", status=405)

def logout(request):
    if request.method == 'POST':
        from django.contrib.auth import logout as auth_logout
        auth_logout(request)
        return redirect("users:login")

    return HttpResponse("Method not allowed", status=405)

def profile(request):
    if request.method == 'POST':
        form_type = request.POST.get("form_type")

        if form_type == "profile":
            form = ProfileForm(request.POST, instance=request.user)
            if form.is_valid():
                form.save()
                messages.success(request, "Profile updated successfully.")
                return redirect("users:profile")
            else:
                messages.error(request, "Please correct the errors below.")
                return render(request, 'profile.html', {'profile_form': form})
        if form_type == "password":
            form = PasswordChangeForm(request.user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "Password changed successfully.")
                return redirect("users:profile")
            else:
                messages.error(request, "Please correct the errors below.")
                return render(request, 'profile.html', {'password_form': form})
        return HttpResponse("Invalid form submission", status=400)

    if request.method == 'GET':
        return render(request, 'profile.html', {
            'profile_form': ProfileForm(instance=request.user),
            'password_form': PasswordChangeForm(user=request.user),
        })

    return HttpResponse("Method not allowed", status=405)