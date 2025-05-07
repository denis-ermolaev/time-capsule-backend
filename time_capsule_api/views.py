from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin, CreateModelMixin, RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin
from .models import CapsulesModel
from .serializers import CapsulesSerializer


class CapsuleView(GenericViewSet, ListModelMixin, CreateModelMixin, RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin):
    queryset = CapsulesModel.objects.all()
    serializer_class = CapsulesSerializer
    lookup_field = 'pk'