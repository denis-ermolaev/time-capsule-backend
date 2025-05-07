from django.urls import path
from time_capsule_api.views import  CapsuleView


urlpatterns = [
    path('capsules', CapsuleView.as_view({'get': 'list', 'post': 'create'}), name='capsule-list'),
    path('capsules/<int:pk>/', CapsuleView.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='capsule-detail'),
]