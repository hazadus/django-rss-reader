from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """
    Custom user model with additional fields.
    """

    profile_image = models.ImageField(
        verbose_name="profile image",
        null=True,
        blank=True,
        upload_to="images/profiles/",
    )

    def __str__(self):
        return self.username
