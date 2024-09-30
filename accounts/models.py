''' accounts/models.py '''

from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.mail import send_mail
from django.core.validators import RegexValidator

class TimestampedModel(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_('The Email must be set'))  # Utilisation de _ pour internationaliser
        if password is None:
            raise ValueError(_('The Password must be set'))  # Utilisation de _ pour internationaliser
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))  # Utilisation de _ pour internationaliser
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))  # Utilisation de _ pour internationaliser
        return self.create_user(email, password, **extra_fields)

name_validator = RegexValidator(r'^[a-zA-Z]*$', 'Only alphabets characters are allowed.')

class CustomUser(AbstractUser, TimestampedModel):
    username = None
    email = models.EmailField(_('email address'), unique=True, max_length=255)
    first_name = models.CharField(_('first name'), max_length=255, blank=True, validators=[name_validator])
    last_name = models.CharField(_('last name'), max_length=255, blank=True, validators=[name_validator])
    is_staff = models.BooleanField(_('staff status'), default=False)
    is_active = models.BooleanField(_('active'), default=True)
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        ordering = ('-date_joined',)

    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'.strip()

    def get_short_name(self):
        return self.first_name
    
    def get_initials(self):
        return self.first_name[0].upper() if self.first_name else ''
    
    def __str__(self):
        return self.email
    
    def email_user(self, subject, message, from_email=None, **kwargs):
        '''Sends an email to this User.'''
        send_mail(subject, message, from_email, [self.email], **kwargs)