import base64
import codecs
import datetime
import json
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema_view, extend_schema
from .models import CapsulesModel
from .serializers import CapsulesSerializer
from django.core.cache import cache

from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

from .serializers import CreateUserSerializer
from django.core.exceptions import ObjectDoesNotExist

import subprocess


def encrypt_capsule(capsule, text):
    print(capsule.__dict__)
    args = [
        str(capsule.id),
        "--create",
        f'"{str(base64.b64encode(text.encode()))[2:-1]}"',
        f'"{str(capsule.date_open)[0:19]}"',
        f'"{str(
            capsule.date_create
            if len(capsule.count_change) == 0
            else capsule.count_change[-1]
        )[0:19]}"',
    ]
    if capsule.emergency_access:
        args.append("--emergency")
        args.append("true" if capsule.ea_after_open else "false")
        args.append(f"'{json.dumps(capsule.ea_time_separation)}'")
    if capsule.opening_days_mode:
        args.append("--opening_days_mode")
        args.append(f'"{capsule.day_week_odm}"')
        args.append(str(capsule.num_week_odm))
        args.append(f'"{str(capsule.time_odm_start)[:-3]}"')
        args.append(f'"{str(capsule.time_odm_end)[:-3]}"')
    command = f'"time_capsule_api/create_read_capsules_v2/create_read_capsules_v2.exe" {" ".join(args)}'
    print("command", command)
    result = subprocess.run(
        args=command,
        shell=True,
        check=True,
        capture_output=True,
        text=True,
    )
    return str(result.stdout).split("\n")[:-1]


def open_encrypt_capsule(capsule):
    command = f'"time_capsule_api/create_read_capsules_v2/create_read_capsules_v2.exe" {str(capsule.id)} --read'
    print("command", command)
    result = subprocess.run(
        args=command,
        shell=True,
        check=True,
        capture_output=True,
        text=True,
    )
    result = str(result.stdout).split("\n")[:-1]
    if result[0] == "2":
        result[1] = codecs.decode(base64.b64decode(result[1].encode()))
        # TODO: Добавить тут count открытий капсулы и сохранить модель
    return result


class RegisterAPIView(APIView):

    authentication_classes = []  # Чтобы убрать замок для документации
    serializer_class = CreateUserSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "success"}, status=201)
        return Response({"error": serializer.errors}, status=400)


class CapsuleView(APIView):
    serializer_class = CapsulesSerializer

    class Pagination(PageNumberPagination):
        page_size = 5
        page_size_query_param = "page_size"
        max_page_size = 100

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="private",
                type=bool,
                location=OpenApiParameter.QUERY,
                description="Запросить приватные или публичные капсулы",
            ),
            OpenApiParameter(
                name="page",
                type=int,
                location=OpenApiParameter.QUERY,
                description="Номер страницы",
            ),
            OpenApiParameter(
                name="page_size",
                type=int,
                location=OpenApiParameter.QUERY,
                description="От 5 до 100, размер получаемых данных",
            ),
            OpenApiParameter(
                name="sortBy",
                type=str,
                location=OpenApiParameter.QUERY,
                description="Сортировка по",
                enum=[
                    "title",
                    "-title",
                    "date_create",
                    "-date_create",
                    "date_open",
                    "-date_open",
                    "count_opening",
                    "-count_opening",
                ],
            ),
            OpenApiParameter(
                name="search",
                type=str,
                location=OpenApiParameter.QUERY,
                description="поиск",
            ),
            OpenApiParameter(
                name="relative_open",
                type=str,
                location=OpenApiParameter.QUERY,
                description="Открываются сегодня, на этой недели, в этом месяце( day, week, month )",
                enum=["day", "week", "month"],
            ),
            OpenApiParameter(
                name="open_date",
                type=str,
                location=OpenApiParameter.QUERY,
                description="2025-04-23 - 2026.01.01",
            ),
            OpenApiParameter(
                name="create_date",
                type=str,
                location=OpenApiParameter.QUERY,
                description="2025-04-23 - 2026.01.01",
            ),
            OpenApiParameter(
                name="num_open_lte",
                type=int,
                location=OpenApiParameter.QUERY,
                description="Число открытий меньше ИЛИ равно этому значению",
            ),
        ]
    )
    def get(self, request):
        def filtration(request):
            if request.GET.get("private") == "false":  # Публичная
                capsules = CapsulesModel.objects.filter(private=False)
            else:
                capsules = CapsulesModel.objects.filter(user=request.user)

            if request.GET.get("num_open_less"):
                capsules = capsules.filter(
                    count_opening__lte=request.GET.get("num_open_less")
                )
            if request.GET.get("search"):
                capsules = capsules.filter(title__icontains=request.GET.get("search"))
            if request.GET.get("open_date"):
                open_date_range = request.GET.get("open_date").split(" - ")
                for index, el in enumerate(open_date_range):
                    if index == 0 and len(el) == 0:
                        open_date_range[index] = datetime.datetime.min
                    elif index == 1 and len(el) == 0:
                        open_date_range[index] = datetime.datetime.max
                    else:
                        open_date_range[index] = datetime.datetime.strptime(
                            el, r"%Y-%m-%d"
                        )
                capsules = capsules.filter(
                    date_open__date__range=(open_date_range[0], open_date_range[1])
                )
            if request.GET.get("create_date"):
                create_date_range = request.GET.get("create_date").split(" - ")
                for index, el in enumerate(create_date_range):
                    if index == 0 and len(el) == 0:
                        create_date_range[index] = datetime.datetime.min
                    elif index == 1 and len(el) == 0:
                        create_date_range[index] = datetime.datetime.max
                    else:
                        create_date_range[index] = datetime.datetime.strptime(
                            el, r"%Y-%m-%d"
                        )
                print(create_date_range)
                capsules = capsules.filter(
                    date_create__date__range=(
                        create_date_range[0],
                        create_date_range[1],
                    )
                )
            if request.GET.get("relative_open") and not (request.GET.get("open_date")):
                if request.GET.get("relative_open") == "day":
                    capsules = capsules.filter(
                        date_open__date=datetime.datetime.today()
                    )
                elif request.GET.get("relative_open") == "week":
                    capsules = capsules.filter(
                        date_open__date__range=(
                            datetime.datetime.today(),
                            datetime.datetime.today() + datetime.timedelta(days=7),
                        )
                    )
                elif request.GET.get("relative_open") == "month":
                    capsules = capsules.filter(
                        date_open__date__range=(
                            datetime.datetime.today(),
                            datetime.datetime.today() + datetime.timedelta(days=30),
                        )
                    )
            elif request.GET.get("open_date"):
                if open_date_range[0] != datetime.datetime.max:
                    if request.GET.get("relative_open") == "day":
                        capsules = capsules.filter(date_open__date=open_date_range[0])
                    elif request.GET.get("relative_open") == "week":
                        capsules = capsules.filter(
                            date_open__date__range=(
                                open_date_range[0],
                                open_date_range[0] + datetime.timedelta(days=7),
                            )
                        )
                    elif request.GET.get("relative_open") == "month":
                        capsules = capsules.filter(
                            date_open__date__range=(
                                open_date_range[0],
                                open_date_range[0] + datetime.timedelta(days=30),
                            )
                        )
                elif open_date_range[1] != datetime.datetime.max:
                    if request.GET.get("relative_open") == "day":
                        capsules = capsules.filter(date_open__date=open_date_range[1])
                    elif request.GET.get("relative_open") == "week":
                        capsules = capsules.filter(
                            date_open__date__range=(
                                open_date_range[1],
                                open_date_range[1] + datetime.timedelta(days=7),
                            )
                        )
                    elif request.GET.get("relative_open") == "month":
                        capsules = capsules.filter(
                            date_open__date__range=(
                                open_date_range[1],
                                open_date_range[1] + datetime.timedelta(days=30),
                            )
                        )
            if request.GET.get("sortBy"):
                capsules = capsules.order_by(request.GET.get("sortBy"))
            return capsules

        if request.user.is_anonymous:
            return Response(
                {"error": "Доступно только зарегестрированным пользователям"},
                status=401,
            )
        capsules_list = filtration(request)
        pagination = self.Pagination()
        queryset = pagination.paginate_queryset(queryset=capsules_list, request=request)
        data = self.serializer_class(queryset, many=True)
        return pagination.get_paginated_response(data.data)

    def post(self, request):
        if request.user.is_anonymous:
            return Response(
                {"error": "Доступно только зарегестрированным пользователям"},
                status=401,
            )
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            filed_for_model = serializer.validated_data.copy()
            filed_for_model["text_bd"] = (
                ""  # Пока не сохраняем зашифрованный текст в модели
            )
            new_capsules_row = CapsulesModel(user=request.user, **filed_for_model)
            print("serializer.validated_data", serializer.validated_data)
            new_capsules_row.save()
            result = encrypt_capsule(
                new_capsules_row, serializer.validated_data["text_bd"]
            )
            serializer_res = self.serializer_class(new_capsules_row)
            return Response(
                data={"message": serializer_res.data, "result": result}, status=201
            )
        return Response({"error": serializer.errors}, status=400)


class CapsuleDetailView(APIView):
    serializer_class = CapsulesSerializer

    def get_by_id(self, id):
        try:
            capsule = CapsulesModel.objects.get(id=id)
            return capsule
        except ObjectDoesNotExist:
            return Response(data={"error": "Такой капсулы нет"}, status=404)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="tryOpenCapsule",
                type=bool,
                location=OpenApiParameter.QUERY,
                description="Открыть капсулу или только запросить о ней данные",
            ),
        ]
    )
    def get(self, request, id):
        if request.user.is_anonymous:
            return Response(
                {"error": "Доступно только зарегестрированным пользователям"},
                status=401,
            )
        capsule = self.get_by_id(id)

        serializer = self.serializer_class(capsule)
        if capsule.private or capsule.user_id == request.user:
            if request.GET.get("tryOpenCapsule"):
                responce_encrypt_capsule = open_encrypt_capsule(capsule)
                return Response(
                    data={
                        "message": serializer.data,
                        "result": responce_encrypt_capsule,
                    },
                    status=201,
                )
            else:
                return Response(
                    data={"message": serializer.data},
                    status=201,
                )
        else:
            return Response(data={"error": "У вас нет права доступа"}, status=403)

    def patch(self, request, id):
        if request.user.is_anonymous:
            return Response(
                {"error": "Доступно только зарегестрированным пользователям"},
                status=401,
            )
        capsule = self.get_by_id(id)
        if isinstance(capsule, Response):
            return capsule

        text = request.data["text_bd"]
        request.data["text_bd"] = ""
        serializer = self.serializer_class(capsule, data=request.data, partial=True)

        if capsule.user_id != request.user.username:
            return Response(data={"error": "У вас нет права доступа"}, status=403)
        elif serializer.is_valid():
            serializer.save()
            capsule = self.get_by_id(id)
            result = encrypt_capsule(capsule, text)
            return Response(
                data={"message": serializer.data, "result": result}, status=201
            )
        else:
            return Response(data={"error": serializer.errors}, status=400)

    def delete(self, request, id):
        capsule = self.get_by_id(id)
        if capsule.user_id == request.user:
            capsule.delete()
            return Response(data={"message": "Капсула успешно удалена"}, status=204)
        else:
            return Response(data={"error": "У вас нет права доступа"}, status=403)


class StatisticslView(APIView):
    def get(self, request):
        if request.user.is_anonymous:
            return Response(
                {"error": "Доступно только зарегестрированным пользователям"},
                status=401,
            )
        datetime_now = datetime.datetime.now()
        cache_timeout: datetime.timedelta = (
            datetime.datetime.now().replace(
                day=datetime_now.day + 1, hour=0, minute=0, second=0, microsecond=0
            )
            - datetime_now
        ).total_seconds()

        capsules_all = cache.get("cached_capsules_all")
        if not capsules_all:
            capsules_all = len(CapsulesModel.objects.all())  # Всего капсул
            cache.set("cached_capsules_all", capsules_all, cache_timeout)

        capsules_close = cache.get("cached_capsules_close")
        if not capsules_close:
            capsules_close = len(
                CapsulesModel.objects.filter(
                    date_open__gt=datetime.datetime.now(),
                    emergency_access=False,
                    private=False,
                )
            )  # Закрытые публичные капсулы
            cache.set("cached_capsules_close", capsules_close, cache_timeout)

        capsules_public = cache.get("cached_capsules_public")
        if not capsules_public:
            capsules_public = len(
                CapsulesModel.objects.filter(
                    private=False,
                )
            )  # Для круговой диаграммы соотношений публичных и частных
            cache.set("cached_capsules_public", capsules_public, cache_timeout)

        capsules_private = cache.get("cached_capsules_private")
        if not capsules_private:
            capsules_private = len(
                CapsulesModel.objects.filter(
                    private=True,
                )
            )  #
            cache.set("cached_capsules_private", capsules_private, cache_timeout)

        day_count = cache.get("cached_day_count")
        if not day_count:
            day_count = {}
            capsules = CapsulesModel.objects.only("date_create", "private")
            for capsule in capsules.values():
                if str(capsule["date_create"].date()) in day_count.keys():
                    day_count[str(capsule["date_create"].date())] += 1
                else:
                    day_count[str(capsule["date_create"].date())] = 1
            cache.set("cached_day_count", day_count, cache_timeout)

        return Response(
            data={
                "allCapsules": capsules_all,
                "closeCapsules": capsules_close,
                "publicCapsules": capsules_public,
                "privateCapsules": capsules_private,
                "сolumnСhartDayCount": day_count,
            },
            status=200,
        )
