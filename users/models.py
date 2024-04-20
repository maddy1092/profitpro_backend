from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _
import random;

colors = ['#00BE08', '#FFB526',  '#4256D0', '#DC2626', '#C400E4'] 
class UserManager(BaseUserManager):
  use_in_migrations = True

  def _create_user(self, user_email, **extra_fields):
    if not user_email:
      raise ValueError('Users require an email field')
    email = self.normalize_email(user_email)
    user = self.model(user_email=user_email, **extra_fields)
    user.save(using=self._db)
    return user

  def create_user(self, user_email, **extra_fields):
    extra_fields.setdefault('is_staff', False)
    extra_fields.setdefault('is_superuser', False)
    extra_fields.setdefault('role', 'sales_representative')
    extra_fields.setdefault('state', random.choice(colors))
    return self._create_user(user_email, **extra_fields)

  def create_superuser(self, user_email, **extra_fields):
    extra_fields.setdefault('is_staff', True)
    extra_fields.setdefault('is_superuser', True)
    extra_fields.setdefault('role', 'admin')

    if extra_fields.get('is_staff') is not True:
      raise ValueError('Superuser must have is_staff=True.')
    if extra_fields.get('is_superuser') is not True:
      raise ValueError('Superuser must have is_superuser=True.')

    return self._create_user(user_email, **extra_fields)


class User(AbstractUser):
  username = None
  user_id = models.PositiveIntegerField(primary_key=True)
  user_email = models.EmailField(unique=True)
  user_display_name = models.CharField(max_length=100, blank=True)
  first_name = models.CharField(max_length=100, blank=True)
  last_name = models.CharField(max_length=100, blank=True)
  role = models.CharField(max_length=50, blank=True)
  city = models.CharField(max_length=100, blank=True)
  address1 = models.CharField(max_length=255, blank=True)
  address2 = models.CharField(max_length=255, blank=True)
  about = models.TextField(blank=True)
  dealer_name = models.CharField(max_length=255, blank=True)
  email = models.EmailField(unique=True)
  is_update = models.BooleanField(default=True)
  lot_address = models.CharField(max_length=255, blank=True)
  notes = models.TextField(blank=True)
  phone = models.CharField(max_length=20, blank=True)
  state = models.CharField(max_length=100, blank=True)
  token = models.CharField(max_length=255, blank=True)
  userImage = models.CharField(max_length=255, blank=True)
  user_avatar = models.CharField(max_length=255, blank=True)
  user_nicename = models.CharField(max_length=100, blank=True)
  zipcode = models.CharField(max_length=20, blank=True)
  
  groups = models.ManyToManyField(
    Group,
    verbose_name=_('groups'),
    blank=True,
    related_name='custom_user_set'  # Choose an appropriate name
  )
  user_permissions = models.ManyToManyField(
    Permission,
    verbose_name=_('user permissions'),
    blank=True,
    related_name='custom_user_set_permissions'  # Choose an appropriate name
  )

  objects = UserManager()

  USERNAME_FIELD = 'user_email'
  REQUIRED_FIELDS = []

  def __str__(self):
    return self.user_display_name