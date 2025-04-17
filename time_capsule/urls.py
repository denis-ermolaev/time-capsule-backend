from django.urls import path
from time_capsule import views
from django.urls import path
from django.contrib.auth import views as auth_views

from .views import SignUpView, CustomLoginView

urlpatterns = [
    path('', views.get_home_page),
    path("signup/", SignUpView.as_view(), name="signup"),
    path("login/", CustomLoginView.as_view(redirect_authenticated_user=True, template_name='registration/login.html'), name="loginCustom"),
]
