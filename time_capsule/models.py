from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class Capsules(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='capsules')
    title = models.CharField(max_length=50) # Вводится пользователем
    create_data = models.DateTimeField(unique_for_date=title) # 
    path_capsule = models.CharField(max_length=255, default="Путя пока нет")
    opening_after_date = models.DateTimeField() # Вводится пользователем, после можно продлевать или открыть капсулу после этой даты
    
    class Meta:
        ordering = ['-opening_after_date']
    def __str__(self):
        return self.title[:50]