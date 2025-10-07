from django.db import models
from django.contrib.auth.models import User

class AD(models.Model):
    title = models.CharField(max_length=75)
    body =  models.CharField(max_length=150)
    image = models.ImageField(upload_to='ad_create/')
    date = models.DateTimeField(auto_now_add=True   )
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True)
    price = models.CharField(max_length=15,default='UAH')
