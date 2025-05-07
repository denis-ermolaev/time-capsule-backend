from django.db import models

# Create your models here.
class CapsulesModel(models.Model):
    title = models.CharField(max_length=100)
    date_create = models.DateTimeField(auto_now=True)
    date_open = models.DateTimeField()
    private = models.BooleanField(default=True)
    class Meta:
        ordering = ["-date_create"]