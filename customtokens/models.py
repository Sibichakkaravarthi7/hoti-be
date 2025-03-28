from django.db import models
from django.utils import timezone
from rest_framework.authtoken.models import Token

class CustomToken(Token):
    expire_date = models.DateTimeField(default=timezone.now() + timezone.timedelta(days=7))
    class Meta:
        managed = False
