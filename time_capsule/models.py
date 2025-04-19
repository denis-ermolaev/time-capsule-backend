from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class Capsules(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='capsules')
    title = models.CharField(max_length=255) # Вводится пользователем
    create_data = models.DateTimeField(unique_for_date=title) # 
    opening_after_date = models.DateTimeField() # Вводится пользователем, после можно продлевать или открыть капсулу после этой даты
    
    public_access = models.BooleanField(default=False)
    emergency_access = models.BooleanField(default=False)
    
    ea_time = models.IntegerField(default=0)
    ea_separation = models.IntegerField(default=1)
    class Meta:
        ordering = ['-create_data']
    def __str__(self):
        return self.title[:50]