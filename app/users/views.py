from django.http import HttpResponse
from django.contrib.auth import login as auth_login
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.views import PasswordResetConfirmView
from django.contrib import messages
from django.shortcuts import redirect, render
from .forms import ProfileForm, LoginForm, UserFilterForm, PasswordChangeForm
from audit.services import audit_logger, get_form_changes
from .models import User
from common.views import FilteredListView
from django.contrib.auth.decorators import login_not_required
from django.utils.decorators import method_decorator

# Create your views here.
class UserListView(FilteredListView):
    model = User
    template_name = 'user_list.html'
    context_object_name = 'users'

    filter_form_class = UserFilterForm

    search_fields = (
        "email",
        "first_name",
        "last_name",
    )

    filter_map = {
        "id": "id",
        "role": "role",
    }


def user_details(request, pk):
    user = User.objects.get(pk=pk)
    return render(request, 'user_details.html', {'user': user})

@login_not_required
def login(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()

            auth_login(request, user)

            audit_logger.info(
                "User logged in",
                action="login",
                user_id=user.id,
            )

            return redirect("/")
        # Authentication failed.
        user = None

        email = form.data.get("username")

        if email:
            user = User.objects.filter(email=email).first()

        audit_logger.warning(
            "Failed login attempt",
            extra={
                "audit": {
                    "action": "failed_login",
                    "user_id": user.id if user else None,
                }
            },
        )

    else:
        form = LoginForm(request)

    return render(request, 'login.html', {'form': form})

@login_not_required
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
        print(f"Form type: {form_type}")  # Debugging line

        if form_type == "profile":
            form = ProfileForm(request.POST, instance=request.user)
            if form.is_valid():
                changes = get_form_changes(form)
                form.save()
                messages.success(request, "Profile updated successfully.")
                audit_logger.info(
                    "User updated profile",
                    action="update_profile",
                    user_id=request.user.id,
                    metadata={"changes": changes}
                )
                return redirect("users:profile")
            else:
                messages.error(request, "Please correct the errors below.")
                return render(request, 'profile.html', {'profile_form': form, 'password_form': PasswordChangeForm(user=request.user)})

        if form_type == "password":
            form = PasswordChangeForm(request.user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "Password changed successfully.")
                audit_logger.info(
                    "User changed password",
                    action="change_password",
                    user_id=request.user.id,
                )
                return redirect("users:profile")
            else:
                messages.error(request, "Please correct the errors below.")
                return render(request, 'profile.html', {'password_form': form, 'profile_form': ProfileForm(instance=request.user)})
        return HttpResponse("Invalid form submission", status=400)

    if request.method == 'GET':
        return render(request, 'profile.html', {
            'profile_form': ProfileForm(instance=request.user),
            'password_form': PasswordChangeForm(user=request.user),
        })

    return HttpResponse("Method not allowed", status=405)

@method_decorator(login_not_required, name='dispatch')
class AuditedPasswordResetConfirmView(PasswordResetConfirmView):
    def form_valid(self, form):
        response = super().form_valid(form)
        user = form.user
        audit_logger.info(
            "User reset password",
            action="reset_password",
            user_id=user.id,
        )
        audit_logger.info(
            "User logged in after password reset",
            action="login",
            user_id=user.id,
        )
        return response