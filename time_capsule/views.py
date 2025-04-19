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

@login_required
def get_capsule_detail(request, num):
    if request.method == 'POST':
        capsule = Capsules.objects.filter(user=request.user).get(id=num)
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
        capsule = Capsules.objects.filter(user=request.user).get(id=num)
        result = subprocess.run(f'"time_capsule/create_read_capsules/create_read_capsules.exe" {str(capsule.id)} --read',shell=True, check=True, capture_output = True, text=True)
        capsule_answer = result.stdout
        hanler_text_decode = capsule_answer.split('\n')
        #if 
        #capsule_answer = codecs.decode(base64.b64decode(capsule_answer.split('\n')[-2][2:-1].encode()))
        print(hanler_text_decode)
        form = False
        if 'Капсула не может быть отрыта' not in hanler_text_decode and 'Капсула может быть открыта с помощью экстренного доступа. Запускаем экстренный доступ' not in hanler_text_decode:
            hanler_text_decode[-2] = codecs.decode(base64.b64decode(capsule_answer.split('\n')[-2][2:-1].encode()))
            form = CapsulesForm(instance=capsule, initial={'text':hanler_text_decode[-2]})
        if 'Капсула может быть открыта' in hanler_text_decode:
            hanler_text_decode[-2] = codecs.decode(base64.b64decode(capsule_answer.split('\n')[-2][2:-1].encode()))
            form = CapsulesForm(instance=capsule, initial={'text':hanler_text_decode[-2]})
            
        capsule_answer = "\n".join(hanler_text_decode)
        print(hanler_text_decode)
        return render(request,
                  'time_capsule/detail.html', {"capsule":capsule,"capsule_answer":capsule_answer, "form":form})

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
    success_url = reverse_lazy("login")
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