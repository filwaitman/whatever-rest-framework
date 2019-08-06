from django.db import models


class User(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    first_name = models.CharField(max_length=63)
    last_name = models.CharField(max_length=63)
