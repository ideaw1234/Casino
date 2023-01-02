from django.contrib import messages
from django.contrib.auth.backends import ModelBackend

class CustomAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        # Use the built-in authenticate method to check the username and password
        user = super().authenticate(request, username, password, **kwargs)

        # If the user is not active, add an error message and return None
        if user is not None and not user.is_active:
            messages.error(request, 'Your account is not active. Please contact the site administrator.')
            return None

        return user