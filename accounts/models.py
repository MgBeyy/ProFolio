from django.db import models
from django.contrib.auth.models import User


class UserEmailToken(models.Model):
    user = models.OneToOneField(
        User, related_name="email_token", on_delete=models.CASCADE
    )
    email_verification_token = models.CharField(max_length=50, default="", blank=True)
    email_verification_expire = models.DateTimeField(null=True, blank=True)
    is_verified = models.BooleanField(default=True)

    class Meta:
        verbose_name = "User Email Tokens"
        verbose_name_plural = "Users Email Tokens"
        db_table = "user_email_token"


#  ?: we may need to overwrite the default user model. So let's leave this here for now.
# from django.contrib.auth.models import AbstractUser
# from django.db import models

# class PlatformUser(AbstractUser):
#     email = models.EmailField(
#         unique=True,
#         blank=False,
#         null=False,
#     )

#     USERNAME_FIELD = 'email'

#     def __str__(self):
#         return self.email
