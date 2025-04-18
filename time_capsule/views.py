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


# Create your views here.
def get_home_page(request):
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
            print("Форма сохранена")
        capsulesform = CapsulesForm()
        return render(request,
                  'time_capsule/homepage.html', {'form': capsulesform})
    else:
        capsulesform = CapsulesForm()
        return render(request,
                  'time_capsule/homepage.html', {'form': capsulesform})
    
    
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