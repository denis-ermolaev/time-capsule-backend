from rest_framework import serializers
from .models import CapsulesModel, AccessLogModel
from django.contrib.auth.hashers import make_password

from django.contrib.auth.models import User
from drf_spectacular.utils import extend_schema_serializer, OpenApiExample


class CreateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("username", "password")

    def validate_password(self, value: str) -> str:
        return make_password(value)


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            name="Valid example for CapsulesSerializer",
            summary="Example data for CapsulesSerializer",
            description="This example demonstrates a valid request payload for the CapsulesSerializer.",
            value={
                "text_bd": "Это текста капсулы",
                "title": "My Capsule",
                "description": "Description of the capsule",
                "date_open": "2025-06-01T00:00:00Z",
                "private": True,
                "share_mode": True,
                "emergency_access": False,
                "ea_after_open": True,
                "ea_time_separation": [
                    [[1, 1], "hidden"],
                    [[1, 5], "open"],
                    [[1, 2], "open"],
                ],
                "opening_days_mode": True,
                "day_week_odm": "m,t,w,th,f,sa,su",
                "num_week_odm": 0,
                "time_odm_start": "12:00:00",
                "time_odm_end": "13:30:00",
                "required_access_log": True,
            },
            request_only=True,  # Пример только для запросов
        ),
        OpenApiExample(
            name="Response example for CapsulesSerializer",
            summary="Example of a response payload",
            description="This example demonstrates a valid response payload for the CapsulesSerializer.",
            value={
                "id": 1,
                "title": "My Capsule",
                "description": "Description of the capsule",
                "user": "Name first user",
                "date_create": "2025-05-10T12:34:56Z",
                "date_change": "2025-05-10T12:45:00Z",
                "date_open": "2025-06-01T00:00:00Z",
                "content_rating_ai": 0,
                "content_rating": 10,
                "private": True,
                "share_mode": True,
                "share_link": "OzWTEqU73rOsS3KQWculxAd4ZQky0LlbiSOC0ocRooEJ2M570VdwJJazMggMTNLPfgASPXbuolT76gCoVnuRvE7xiONOSahtu1cN",
                "emergency_access": False,
                "ea_after_open": True,
                "ea_time_separation": [
                    [[1, 1], "hidden"],
                    [[1, 5], "open"],
                    [[1, 2], "open"],
                ],
                "count_opening": 3,
                "count_change": ["2025-05-15 18:25:37", "2025-05-15 18:26:28"],
                "opening_days_mode": True,
                "day_week_odm": "m,t,w,th,f,sa,su",
                "num_week_odm": 2,
                "time_odm_start": "12:00:00",
                "time_odm_end": "13:30:00",
                "required_access_log": True,
            },
            response_only=True,  # Пример только для ответов
        ),
    ]
)
class CapsulesSerializer(serializers.ModelSerializer):

    class Meta:
        model = CapsulesModel
        fields = (
            "id",
            "title",
            "description",
            "user",
            "date_create",
            "date_change",
            "date_open",
            "content_rating_ai",
            "content_rating",
            "private",
            "share_mode",
            "share_link",
            "share_password",
            "text_bd",
            "emergency_access",
            "ea_after_open",
            "ea_time_separation",
            "count_opening",
            "count_change",
            "opening_days_mode",
            "day_week_odm",
            "num_week_odm",
            "time_odm_start",
            "time_odm_end",
            "required_access_log",
        )
        extra_kwargs = {
            "id": {"read_only": True},
            "date_create": {"read_only": True},
            "date_change": {"read_only": True},
            "user": {"read_only": True},
            "date_change": {"read_only": True},
            "count_opening": {"read_only": True},
            "count_change": {"read_only": True},
            "content_rating_ai": {"read_only": True},
            "content_rating": {"read_only": True},
            "share_link": {"read_only": True},
            "text_bd": {"required": True},
        }

    def validate_ea_time_separation(self, value: list) -> list:
        if not isinstance(value, list):
            raise serializers.ValidationError(
                "Поле ea_time_separation должно быть списком."
            )

        for entry in value:
            if not isinstance(entry, list) or len(entry) != 2:
                raise serializers.ValidationError(
                    "Каждый элемент ea_time_separation должен быть списком из двух элементов."
                )
            if not isinstance(entry[0], list) or not isinstance(entry[1], str):
                raise serializers.ValidationError(
                    "Первый элемент в каждом подсписке должен быть int или float, а второй - str."
                )
            if entry[1] not in ["hidden", "open"]:
                raise serializers.ValidationError(
                    "Второй элемент в каждом подсписке должен быть либо 'hidden', либо 'open'."
                )
            if not isinstance(entry[0][0], (int, float)) or not isinstance(
                entry[0][1], (int, float)
            ):
                raise serializers.ValidationError(
                    "Первый элемент должен содержать список с цифрами(int,float) - диапазон разброса случайного времени"
                )
        return value


class AccessLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccessLogModel
        fields = ["capsule", "date", "text", "access_assessment"]
        extra_kwargs = {
            "capsule": {"read_only": True},
            "date": {"read_only": True},
        }
