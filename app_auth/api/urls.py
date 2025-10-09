from django.urls import path
from .views import RegisterView, ActivateView

urlpatterns = [
    path('api/register/', RegisterView.as_view()),
    path('api/activate/<uidb64>/<token>/', ActivateView.as_view()),
]