from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView



urlpatterns = [
    path('', SpectacularSwaggerView.as_view(url_name='schema')),
    path('schema/', SpectacularAPIView.as_view() ,name='schema'),
    path('admin/', admin.site.urls),
    path('users', include('users.urls')),
    path('transcript', include('conversations.urls')),
]
