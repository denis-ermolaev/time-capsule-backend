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

@login_required
def get_capsule_detail(request, num):
    if request.method == 'POST':
        capsule = Capsules.objects.filter(user=request.user).get(id=num)
        form = CapsulesForm(request.POST, instance=capsule)
        if form.is_valid():
            form.save()
            return redirect(to='/detail/'+str(num))

    else:
        capsule = Capsules.objects.filter(user=request.user).get(id=num)
        if timezone.now() > capsule.opening_after_date: # True, если капсулу уже можно открыть
            # TODO: тут проверка реально ли капсулу можно открыть или возможно дата в django была изменена
            # Если можно надо добавить форму для изменения
            capsulesform = CapsulesForm(instance=capsule)
            return render(request,
                  'time_capsule/detail.html', {"capsule":capsule,"can_open":True,"form":capsulesform})
        else:
            return render(request,
                  'time_capsule/detail.html', {"capsule":capsule, "can_open":False})
# Create your views here.
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
                                        opening_after_date = form.cleaned_data['opening_after_date'])
            new_capsules_row.save()
            print("ID текущей капсулы:",new_capsules_row.id)
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