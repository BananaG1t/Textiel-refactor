from django.shortcuts import redirect


class AuthenticationMiddleware:
    EXEMPT_URLS = {
    }

    EXEMPT_URL_PREFIXES = (
        "/i18n",
    )

    GUEST_ONLY_URLS = {
        "/users/login",
        "/users/forgot_password",
    }

    GUEST_ONLY_URL_PREFIXES = (
        "/users/reset_password/",
    )

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if self._is_exempt(request.path):
            return self.get_response(request)

        if self._is_guest_only(request.path) and self._is_valid_user(request.user):
            return redirect("home:home")

        if not self._is_valid_user(request.user) and not self._is_guest_only(request.path):
            return redirect("users:login")

        return self.get_response(request)

    def _is_valid_user(self, user):
        return user.is_authenticated and user.is_active
    
    def _is_exempt(self, path: str):
        return path in self.EXEMPT_URLS or path.startswith(self.EXEMPT_URL_PREFIXES)

    def _is_guest_only(self, path: str):
        return path in self.GUEST_ONLY_URLS or path.startswith(self.GUEST_ONLY_URL_PREFIXES)