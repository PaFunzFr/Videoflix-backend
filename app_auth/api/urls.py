from django.urls import path
from .views import RegisterView, ActivateView, RequestPasswordResetView, ConfirmPasswordView

urlpatterns = [
    path('register/', RegisterView.as_view(), name="register"),
    path('activate/<uidb64>/<token>/', ActivateView.as_view(), name="activate"),

    path('password_reset/', RequestPasswordResetView.as_view(), name="reset"),
    path('password_confirm/<uidb64>/<token>/', ConfirmPasswordView.as_view(), name="confirm-password"),

    
]

