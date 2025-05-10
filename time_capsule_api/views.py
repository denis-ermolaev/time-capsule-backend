import datetime
from turtle import title
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema_view, extend_schema
from .models import CapsulesModel
from .serializers import CapsulesSerializer
    
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

from .serializers import CreateUserSerializer
from django.core.exceptions import ObjectDoesNotExist


class RegisterAPIView(APIView):
    
    authentication_classes = []  # Чтобы убрать замок для документации
    serializer_class = CreateUserSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': "success"}, status=201)
        return Response({"error": serializer.errors}, status=400)


class CapsuleView(APIView):
    serializer_class = CapsulesSerializer
    
    class Pagination(PageNumberPagination):
        page_size = 5
        page_size_query_param = 'page_size'
        max_page_size = 100
    
    
    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="private",
                type=bool,
                location=OpenApiParameter.QUERY,
                description="Запросить приватные или публичные капсулы"
            ),
            OpenApiParameter(
                name="page",
                type=int,
                location=OpenApiParameter.QUERY,
                description="Номер страницы"
            ),
            OpenApiParameter(
                name="page_size",
                type=int,
                location=OpenApiParameter.QUERY,
                description="От 5 до 100, размер получаемых данных"
            ),
            OpenApiParameter(
                name="sortBy",
                type=str,
                location=OpenApiParameter.QUERY,
                description="Сортировка по",
                enum=["title","-title","date_create", "-date_create", "date_open", "-date_open", "count_opening", "-count_opening"],
            ),
            OpenApiParameter(
                name="search",
                type=str,
                location=OpenApiParameter.QUERY,
                description="поиск"
            ),
            OpenApiParameter(
                name="relative_open",
                type=str,
                location=OpenApiParameter.QUERY,
                description="Открываются сегодня, на этой недели, в этом месяце( day, week, month )",
                enum=["day","week","month"],
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
                description="2025-04-23 - 2026.01.01"
            ),
            OpenApiParameter(
                name="num_open_lte",
                type=int,
                location=OpenApiParameter.QUERY,
                description="Число открытий меньше ИЛИ равно этому значению"
            ),
        ]
    )
    def get(self, request):
        def filtration(request):
            if request.GET.get('private') == "false": #Публичная
                capsules = CapsulesModel.objects.filter(private=False)
            else:
                capsules = CapsulesModel.objects.filter(user=request.user)
            
            if request.GET.get('num_open_less'):
                capsules = capsules.filter(count_opening__lte = request.GET.get('num_open_less'))
            if request.GET.get('search'):
                capsules = capsules.filter(title__icontains = request.GET.get('search'))
            if request.GET.get('open_date'):
                open_date_range = request.GET.get('open_date').split(" - ")
                for index, el in enumerate(open_date_range):
                    if index == 0 and len(el) == 0:
                        open_date_range[index] = datetime.datetime.min
                    elif index == 1 and len(el) == 0:
                        open_date_range[index] = datetime.datetime.max
                    else:
                        open_date_range[index] = datetime.datetime.strptime(el, r'%Y-%m-%d')
                capsules = capsules.filter(date_open__date__range = (open_date_range[0], open_date_range[1]))
            if request.GET.get('create_date'):
                create_date_range = request.GET.get('create_date').split(" - ")
                for index, el in enumerate(create_date_range):
                    if index == 0 and len(el) == 0:
                        create_date_range[index] = datetime.datetime.min
                    elif index == 1 and len(el) == 0:
                        create_date_range[index] = datetime.datetime.max
                    else:
                        create_date_range[index] = datetime.datetime.strptime(el, r'%Y-%m-%d')
                print(create_date_range)
                capsules = capsules.filter(date_create__date__range = (create_date_range[0], create_date_range[1]))
            if request.GET.get('relative_open') and not (request.GET.get('open_date')):
                if request.GET.get('relative_open') == "day":
                    capsules = capsules.filter(date_open__date = datetime.datetime.today())
                elif request.GET.get('relative_open') == "week":
                    capsules = capsules.filter(date_open__date__range = (datetime.datetime.today(), datetime.datetime.today() + datetime.timedelta(days=7)) )
                elif request.GET.get('relative_open') == "month":
                    capsules = capsules.filter(date_open__date__range = (datetime.datetime.today(), datetime.datetime.today() + datetime.timedelta(days=30)) )
            elif request.GET.get('open_date'):
                if open_date_range[0] != datetime.datetime.max:
                    if request.GET.get('relative_open') == "day":
                        capsules = capsules.filter(date_open__date = open_date_range[0])
                    elif request.GET.get('relative_open') == "week":
                        capsules = capsules.filter(date_open__date__range = (open_date_range[0], open_date_range[0] + datetime.timedelta(days=7)) )
                    elif request.GET.get('relative_open') == "month":
                        capsules = capsules.filter(date_open__date__range = (open_date_range[0], open_date_range[0] + datetime.timedelta(days=30)) )
                elif open_date_range[1] != datetime.datetime.max:
                    if request.GET.get('relative_open') == "day":
                        capsules = capsules.filter(date_open__date = open_date_range[1])
                    elif request.GET.get('relative_open') == "week":
                        capsules = capsules.filter(date_open__date__range = (open_date_range[1], open_date_range[1] + datetime.timedelta(days=7)) )
                    elif request.GET.get('relative_open') == "month":
                        capsules = capsules.filter(date_open__date__range = (open_date_range[1], open_date_range[1] + datetime.timedelta(days=30)) )
            if request.GET.get('sortBy'):
                capsules = capsules.order_by(request.GET.get('sortBy'))
            return capsules
        
        
        if request.user.is_anonymous:
            return Response({"error":"Доступно только зарегестрированным пользователям"}, status=401)
        capsules_list = filtration(request)
        pagination = self.Pagination()
        queryset = pagination.paginate_queryset(queryset = capsules_list, request = request)
        data = self.serializer_class(queryset, many = True)
        return pagination.get_paginated_response(data.data)
        

    def post(self, request):
        if request.user.is_anonymous:
            return Response({"error":"Доступно только зарегестрированным пользователям"}, status=401)
        serializer  = self.serializer_class(data=request.data)
        if serializer.is_valid():
            new_capsules_row = CapsulesModel(user = request.user, **serializer.validated_data)
            new_capsules_row.save()
            serializer_res  = self.serializer_class(new_capsules_row)
            return Response(data={"message": serializer_res.data}, status=201)
        return Response({"error": serializer.errors}, status=400)
class CapsuleDetailView(APIView):
    serializer_class = CapsulesSerializer
    
    def get_by_id(self, id):
        try:
            capsule = CapsulesModel.objects.get(id=id)
            return capsule
        except ObjectDoesNotExist:
            return Response(data = {"error": "Такой капсулы нет"} , status=404)
        
    def get(self, request, id):
        if request.user.is_anonymous:
            return Response({"error":"Доступно только зарегестрированным пользователям"}, status=401)
        capsule = self.get_by_id(id)
        serializer = self.serializer_class(capsule)
        if capsule.private or capsule.user_id == request.user:
                return Response(data = {"message": serializer.data} , status=201)
        else:
            return Response(data = {"error": "У вас нет права доступа"} , status=403)

    def patch(self, request, id):
        if request.user.is_anonymous:
            return Response({"error":"Доступно только зарегестрированным пользователям"}, status=401)
        capsule = self.get_by_id(id)
        serializer = self.serializer_class(capsule, data=request.data, partial=True)
        if capsule.user_id != request.user.username:
            return Response(data = {"error": "У вас нет права доступа"} , status=403)
        elif serializer.is_valid():
            serializer.save()
            return Response(data = {"message": serializer.data} , status=201)
        else:
            return Response(data = {"error": serializer.errors} , status=400)
        
    def delete(self, request, id):
        capsule = self.get_by_id(id)
        if capsule.user_id == request.user:
            capsule.delete()
            return Response(data = {"message": "Капсула успешно удалена"}, status=204)
        else:
            return Response(data = {"error": "У вас нет права доступа"} , status=403)