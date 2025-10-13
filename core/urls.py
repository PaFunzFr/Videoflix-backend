"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from app_auth.api.views import RegisterView, ActivateView, RequestPasswordResetView, ConfirmPasswordView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('django-rq/', include('django_rq.urls')),

    path('api/register/', RegisterView.as_view(), name="register"),
    path('api/activate/<uidb64>/<token>/', ActivateView.as_view(), name="activate"),

    path('api/password_reset/', RequestPasswordResetView.as_view(), name="reset"),
    path('api/password_confirm/<uidb64>/<token>/', ConfirmPasswordView.as_view(), name="confirm-password"),
]

urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)