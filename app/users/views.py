from django.http import HttpResponse
from django.contrib.auth import login as auth_login
from django.contrib.auth.forms import PasswordChangeForm, PasswordResetForm
from django.contrib import messages
from django.shortcuts import redirect, render
from .forms import ProfileForm, LoginForm

# Create your views here.
def view_users(request):
    return render(request, 'users.html')

def login(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            auth_login(request, form.get_user())
            return redirect("/")

    else:
        form = LoginForm(request)

    return render(request, 'login.html', {'form': form})

def forgot_password(request):
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            form.save(
                request=request,
                use_https=request.is_secure(),
            )

            messages.success(
                request,
                "If an account exists with this email address, "
                "you will receive a password reset link.",
            )
            return redirect("users:forgot_password")

    else:
        form = PasswordResetForm()

    return render(request, 'forgot_password.html', {'form': form})

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