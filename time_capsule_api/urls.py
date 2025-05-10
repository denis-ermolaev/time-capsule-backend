from django.urls import path
from time_capsule_api.views import  CapsuleView, RegisterAPIView, CapsuleDetailView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

urlpatterns = [
    path('auth/', RegisterAPIView.as_view(), name='registration'),
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('capsules', CapsuleView.as_view(), name='capsule-list'),
    path('capsules/<int:id>', CapsuleDetailView.as_view(), name='capsule-detail'),
]