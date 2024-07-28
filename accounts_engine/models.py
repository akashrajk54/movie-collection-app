import time
from django.db import models
from django.contrib.auth.models import AbstractUser
from accounts_engine.managers import CustomUserManager
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField


class BaseClass(models.Model):
    id = models.AutoField(primary_key=True)
    created_datetime = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_datetime = models.DateTimeField(auto_now=True, null=True, blank=True)
    is_delete = models.BooleanField(default=False)
    deleted_datetime = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True


class CustomUser(AbstractUser, BaseClass):
    objects = CustomUserManager()

    username = models.CharField(_("username"), max_length=50, unique=True, blank=True, null=True)
    about = models.CharField(max_length=255, null=True, blank=True)
    contact = PhoneNumberField(
        verbose_name=_("Phone Number"),
        unique=True,
        help_text=_("Enter phone number in international format, e.g., +12122222222"),
        null=True,
        blank=True,
    )
    deleted_contact_number = models.CharField(null=True, blank=True)
    is_active = models.BooleanField(_("active"), default=True)
    is_admin = models.BooleanField(default=False)

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        constraints = [
            models.UniqueConstraint(
                fields=["username", "is_delete"],
                name="unique_customuser_username_is_delete",
            )
        ]

    def __str__(self):
        return f"{self.username} | {self.contact}"

    def save(self, *args, **kwargs):
        if self.is_delete and not self.contact.endswith("_deleted"):

            # Store the original contact number in deleted_contact_number
            self.deleted_contact_number = self.contact

            # Modify the contact field with the timestamp
            self.contact += f"_time_{int(time.time())}_deleted"

        super(CustomUser, self).save(*args, **kwargs)


class InvalidatedToken(models.Model):
    token = models.TextField(unique=True)
    invalidated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Token: {self.token} | Invalidated at: {self.invalidated_at}"
