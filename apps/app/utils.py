from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.models import User


token_generator = PasswordResetTokenGenerator()

def generate_reset_password_link(user, request):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = token_generator.make_token(user)
    reset_link = request.build_absolute_uri(
        reverse("reset_page",args=[uid,token])
    )
    # reset_link = f"http://{request.get_host()}/reset-page/{uid}/{token}/"
    return reset_link


# def generate_reset_password_link(user,request):
#     uid = urlsafe_base64_encode(force_bytes(user.pk))
#     token = token_generator.make_token(user)
#     reset_link = f"http://127.0.0.1:8000/reset-password/?uid={uid}&token={token}"
#     # reset_link = f"127.0.0.1:8000/reset-password/{uid}/{token}/"
#     # reset_link = f"http://{request.get_host()}/reset-password/{uid}/{token}/"
#     return reset_link