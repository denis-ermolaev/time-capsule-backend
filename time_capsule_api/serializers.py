from rest_framework import serializers
from .models import CapsulesModel

class CapsulesSerializer(serializers.ModelSerializer):
    class Meta:
        model = CapsulesModel
        fields = ('id', "title", "date_open", "private")
        