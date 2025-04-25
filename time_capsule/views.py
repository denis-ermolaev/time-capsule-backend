from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views import generic

from django.contrib.auth.views import LoginView
from .forms import LoginForm

from django.shortcuts import render, get_object_or_404
from .forms import CapsulesForm

from .models import Capsules

#import datetime
from django.utils import timezone


from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


from django.contrib.auth.decorators import login_required


from django.shortcuts import redirect


import subprocess
import base64
import codecs

from django.http import JsonResponse

@login_required
def api_get_private_capsule(request):
    def is_ajax(request):
        return request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    if is_ajax(request): # "Type-Capsule": typeCapsule, // "Private" "Public" request.GET.get('open')
        if str(request.user) != "AnonymousUser":
            print("request.GET", request.GET)
            print("request.GET.get('typeCapsule')", request.GET.get('typeCapsule'))
            if request.GET.get('typeCapsule') == 'Private':
                print(request.GET.get('sorted_by'), type(request.GET.get('sorted_by')))
                capsules_list = Capsules.objects.filter(user=request.user).order_by(request.GET.get('sorted_by'))
            else:
                capsules_list = Capsules.objects.filter(public_access=True).order_by(request.GET.get('sorted_by')) # Тут может быть ошибка
                
            if request.GET.get('search'):
                capsules_list = capsules_list.filter(title__icontains=request.GET.get('search'))
            paginator = Paginator(capsules_list, 10)
            page_number = int(request.GET.get('page'))
            print("page_number", page_number)
            try:
                capsules = paginator.page(page_number)
            except PageNotAnInteger:
            # Если page_number не целое число, то
            # выдать первую страницу
                capsules = paginator.page(1)
            except EmptyPage:
            # Если page_number находится вне диапазона, то
            # выдать последнюю страницу результатов
                capsules = paginator.page(paginator.num_pages)
            page_num = str(capsules)
            result_list = []
            previous_page_number = capsules.has_previous()
            next_page_number = capsules.has_next()
            current_num_page = capsules.number
            num_all_page = paginator.num_pages
            for capsule in capsules:
                result_list.append([str(capsule.title),str(capsule.opening_after_date), str(capsule.create_data), str(capsule.id)])
            return JsonResponse({
                'capsules_page': page_num,
                "capsules": result_list,
                "previous_page_number": previous_page_number,
                "next_page_number": next_page_number,
                "current_num_page": current_num_page,
                "num_all_page": num_all_page
            }, status=200)
            # except:
            #     print("api_get_private_capsule возвращает 404")
            #     return JsonResponse({
            #         'capsules': False,
            #     }, status=404)
        else:
            return JsonResponse({
                'capsules': False,
            }, status=404)

    return redirect(to='homepage')
    

def api_get_time(request):
    def is_ajax(request):
        return request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    if is_ajax(request):
        return JsonResponse({
            'time_now': str(timezone.localtime()),
        }, status=200)

    return redirect(to='homepage')

@login_required
def get_capsule_detail(request, num):
    print(request.GET.get('open') is not None)
    if request.method == 'POST':
        #capsule = Capsules.objects.filter(user=request.user).get(id=num)
        capsule = get_object_or_404(Capsules, user=request.user, id=num)
        form = CapsulesForm(request.POST, instance=capsule)
        # TODO: тут по идее должен быть функционал создания новой капсулы
        if form.is_valid():
            form.save()
            print("ID текущей капсулы:",capsule.id)
            print("form.cleaned_data['text'].encode()", form.cleaned_data['text'].encode())
            print("base64.b64encode(form.cleaned_data['text'].encode()", base64.b64encode(form.cleaned_data['text'].encode()))
            result = subprocess.run(f'"time_capsule/create_read_capsules/create_read_capsules.exe" {str(capsule.id)} --create "{base64.b64encode(form.cleaned_data['text'].encode())}" "{str(form.cleaned_data['opening_after_date'])[0:19]}" {str(form.cleaned_data['emergency_access'])} {str(form.cleaned_data['ea_time'])} {str(form.cleaned_data['ea_separation'])}',shell=True, check=True, capture_output = True, text=True)
            #result = subprocess.run(f'"time_capsule/create_read_capsules/create_read_capsules.exe" {str(new_capsules_row.id)} --create "{codecs.encode(form.cleaned_data['text'])}" "{str(form.cleaned_data['opening_after_date'])[0:19]}" {str(form.cleaned_data['emergency_access'])} {str(form.cleaned_data['ea_time'])} {str(form.cleaned_data['ea_separation'])}',shell=True, check=True, capture_output = True, text=True)

            print(result)
            
            return redirect(to='/detail/'+str(num))
    else:
        if request.GET.get('open') is not None:
            # Первая строка, статус
            # 1 - Доступ запрещён, капсула не открыта ИЛИ успешное создание капсулы
            # 2 - Текст получен, по времени или экстренному доступу
            # 3 - Экстренный доступ, + 1 попытка
            # 4 - время захода не правильное
            # 5 - экстренный доступ запрошен, время назначено
            # print("2")
            # print(self.final_console_output["text"])
            
            # print(self.final_console_output["num_access"])
            # print(self.final_console_output["start_limit"])
            # print(self.final_console_output["end_limit"])
            capsule = get_object_or_404(Capsules, id=num) #user=request.user, 
            result = subprocess.run(f'"time_capsule/create_read_capsules/create_read_capsules.exe" {str(capsule.id)} --read',shell=True, check=True, capture_output = True, text=True)
            capsule_answer = result.stdout.split('\n')
            form = False
            if capsule_answer[0] == "1":
                ready_capsule_answer = "Капсула не может быть открыта. Т.к. экстренный доступ не настроен, а время открытия не настало"
            elif capsule_answer[0] == "2":
                ready_capsule_answer = codecs.decode(base64.b64decode(capsule_answer[1][2:-1].encode()))
                form = CapsulesForm(instance=capsule, initial={'text':ready_capsule_answer})
            elif capsule_answer[0] == "3":
                ready_capsule_answer = f"""Экстренный доступ подтверждён \nОсталось подтверждений: {capsule.ea_separation - int(capsule_answer[1])} \nНовое время подтверждения экстренного доступа \nC {capsule_answer[2]} до {capsule_answer[3]}"""
            elif capsule_answer[0] == "4":
                ready_capsule_answer = f"""Вы подтвердили запрос экстренного доступа в неправильное время \nВам назначено новое время подтверждения экстренного доступа \nC {capsule_answer[2]} до {capsule_answer[3]}"""
            elif capsule_answer[0] == "5":
                ready_capsule_answer = f"""Вам нужно будет подтвердить запрос экстренного доступа \nДля этого нужно зайти на эту страницу во время: \nC {capsule_answer[2]} до {capsule_answer[3]}"""
            if str(request.user) == str(capsule.user):
                user_can_delete = True
            else:
                user_can_delete = False
            return render(request,
                      'time_capsule/detail.html', {"capsule":capsule,"capsule_answer":ready_capsule_answer, "form":form, "current_url":'/detail/'+str(num),"user_can_delete":user_can_delete})
        else:
            capsule = get_object_or_404(Capsules, id=num) #user=request.user, 
            return render(request,
                    'time_capsule/detail.html', {"capsule":capsule, "current_url":'/detail/'+str(num)})

def get_home_page(request):
    def draw_homepage(request):
        if str(request.user) != "AnonymousUser":
            print("Скрипт идёт по пути зарегестрированного пользователя")
            capsulesform = CapsulesForm()
            capsules_list = Capsules.objects.filter(user=request.user)
            paginator = Paginator(capsules_list, 10)
            page_number = request.GET.get('page')
            try:
                capsules = paginator.page(page_number)
            except PageNotAnInteger:
            # Если page_number не целое число, то
            # выдать первую страницу
                capsules = paginator.page(1)
            except EmptyPage:
            # Если page_number находится вне диапазона, то
            # выдать последнюю страницу результатов
                capsules = paginator.page(paginator.num_pages)
            return render(request,
                      'time_capsule/homepage.html', {'form': capsulesform, 'capsules': capsules})
        else:
            return render(request,
                      'time_capsule/homepage.html')
        
        
    if request.method == 'POST':
        form = CapsulesForm(request.POST)
        print(request.POST, request.user)
        
        if form.is_valid(): # Соответсвует ли модели ?
            print(form.cleaned_data, request.user)
            # Тут реализация создания с помощью сторонней программы папки с зашифрованным
            # Датой и текстом, после получаем путь
            new_capsules_row = Capsules(user = request.user, 
                                        title = form.cleaned_data['title'],
                                        create_data = timezone.now(), 
                                        opening_after_date = form.cleaned_data['opening_after_date'],
                                        public_access = form.cleaned_data['public_access'],
                                        emergency_access = form.cleaned_data['emergency_access'],
                                        ea_time = form.cleaned_data['ea_time'],
                                        ea_separation = form.cleaned_data['ea_separation'],
                                        )
            new_capsules_row.save()
            print("ID текущей капсулы:",new_capsules_row.id)
            print("form.cleaned_data['text'].encode()", form.cleaned_data['text'].encode())
            print("base64.b64encode(form.cleaned_data['text'].encode()", base64.b64encode(form.cleaned_data['text'].encode()))
            var1 = base64.b64encode(form.cleaned_data['text'].encode())
            print("Декодированная строка в байтах ?", base64.b64decode(var1))
            result = subprocess.run(f'"time_capsule/create_read_capsules/create_read_capsules.exe" {str(new_capsules_row.id)} --create "{base64.b64encode(form.cleaned_data['text'].encode())}" "{str(form.cleaned_data['opening_after_date'])[0:19]}" {str(form.cleaned_data['emergency_access'])} {str(form.cleaned_data['ea_time'])} {str(form.cleaned_data['ea_separation'])}',shell=True, check=True, capture_output = True, text=True)
            #result = subprocess.run(f'"time_capsule/create_read_capsules/create_read_capsules.exe" {str(new_capsules_row.id)} --create "{codecs.encode(form.cleaned_data['text'])}" "{str(form.cleaned_data['opening_after_date'])[0:19]}" {str(form.cleaned_data['emergency_access'])} {str(form.cleaned_data['ea_time'])} {str(form.cleaned_data['ea_separation'])}',shell=True, check=True, capture_output = True, text=True)

            print(result)
            print("Форма сохранена")
        return draw_homepage(request)
    else:  
        return draw_homepage(request)
    
    
class SignUpView(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy("loginCustom")
    template_name = "registration/signup.html"

class CustomLoginView(LoginView):
    form_class = LoginForm

    def form_valid(self, form):
        remember_me = form.cleaned_data.get('remember_me')

        if not remember_me:
            # Установим время истечения сеанса равным 0 секундам. Таким образом, он автоматически закроет сеанс после закрытия браузера. И обновим данные.
            self.request.session.set_expiry(0)
            self.request.session.modified = True

        # В противном случае сеанс браузера будет таким же как время сеанса cookie "SESSION_COOKIE_AGE", определенное в settings.py
        return super(CustomLoginView, self).form_valid(form)
    
    
def delete(request, id):
    capsule = Capsules.objects.get(user=request.user , id=id)
    capsule.delete()
    return redirect(to = 'homepage')