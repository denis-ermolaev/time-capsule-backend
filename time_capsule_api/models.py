from django.db import models
from django.contrib.auth.models import User
import secrets
import string
from django.core.validators import MinValueValidator, MaxValueValidator
import datetime


class CapsulesModel(models.Model):
    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=100)
    description = models.CharField(
        max_length=1000,
        blank=True,
        null=True,
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="capsulesAPI", to_field="username"
    )

    date_create = models.DateTimeField(auto_now_add=True)
    date_change = models.DateTimeField(auto_now=True)
    date_open = models.DateTimeField()

    content_rating_ai = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(10.0)],
        blank=True,
        null=True,
    )
    content_rating = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(10.0)],
        blank=True,
        null=True,
    )

    private = models.BooleanField(default=True)

    # Для частных капсул можно установить share режим, чтобы
    # Делится капсулой по ссылке и паролю
    share_mode = models.BooleanField(default=False)
    share_link = models.CharField(
        max_length=255,
        unique=True,
        blank=True,
        null=True,
    )
    share_password = models.CharField(
        max_length=255,
        blank=True,
        null=True,
    )

    text_bd = models.TextField(
        blank=True,
        null=True,
    )

    emergency_access = models.BooleanField(default=False)
    # Не сбрасывать время при неправильных заходах
    # Также время заранее не видно
    ea_after_open = models.BooleanField(default=False)
    # [ [ [1, 1], 'hidden'], [ [1, 5] , 'open'], [ [0.5,0.5], 'open'] ]
    # После первого запроса ЭД, надо подождать 1 час, потом 1-5 часов, а потом ещё 30 минут
    ea_time_separation = models.JSONField(default=list)

    count_opening = models.IntegerField(default=0)
    count_change = models.JSONField(default=list)

    # Режим, когда капсула открывается только в какие-то дни недели
    # Раз в сколько-то недель на определённые часы
    opening_days_mode = models.BooleanField(default=False)
    # m,t,w,th,f,sa,su - через запятую перечисление дней
    day_week_odm = models.CharField(max_length=30, blank=True, null=True)
    num_week_odm = models.IntegerField(default=0, blank=True, null=True)
    time_odm_start = models.TimeField(blank=True, null=True)
    time_odm_end = models.TimeField(blank=True, null=True)

    required_access_log = models.BooleanField(default=False)

    class Meta:
        ordering = ["-date_create"]

    def generate_unique_share_link(self):
        while True:
            # Генерация случайной строки
            link = "".join(
                secrets.choice(string.ascii_letters + string.digits) for _ in range(100)
            )
            # Проверяем, существует ли уже такое значение в базе данных
            if not CapsulesModel.objects.filter(share_link=link).exists():
                return link

    def save(self, *args, **kwargs):
        if not self.share_link:
            self.share_link = self.generate_unique_share_link()
        if not self.share_password:
            self.share_password = "".join(
                secrets.choice(string.ascii_letters + string.digits) for _ in range(100)
            )
        # Получаем текущее время
        current_time = datetime.datetime.now().strftime(r"%Y-%m-%d %H:%M:%S")

        # Добавляем текущее время в count_change
        # Проверяем, что объект не создаётся (а обновляется)
        if not self._state.adding:
            self.count_change.append(current_time)
        super().save(*args, **kwargs)


class AccessLogModel(models.Model):
    capsule = models.ForeignKey(
        CapsulesModel, on_delete=models.CASCADE, related_name="access_log"
    )
    date = models.DateTimeField(auto_now_add=True)
    text = models.TextField(default="")
    access_assessment = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(10.0)],
    )

    class Meta:
        ordering = ["-date"]
