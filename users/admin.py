
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

class CustomUserAdmin(UserAdmin):
  list_display = ('user_id', 'user_email', 'first_name', 'last_name', 'role', 'state')
  search_fields = ('user_email', 'first_name', 'last_name')
  ordering = ('first_name',)
  fieldsets = (
    (None, {'fields': ('email', 'password')}),
    (('Personal info'), {'fields': ('first_name', 'last_name', 'state', 'user_avatar', 'userImage')}),
    (('Permissions'), {
      'fields': ('is_active', 'is_staff', 'is_superuser', 'user_permissions'),
    }),
    (('Important dates'), {'fields': ('last_login', 'date_joined')}),
  )
  filter_horizontal = ('groups',)
admin.site.register(User, CustomUserAdmin)
