import hashlib
from django.utils import timezone
from django.conf import settings
from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Task(models.Model):
    id = models.CharField(primary_key=True, max_length=64, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    due_date = models.DateTimeField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='tasks')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tasks')
    is_completed = models.BooleanField(default=False)
    
    def save(self, *args, **kwargs):
        if not self.id:
            self.id = hashlib.sha256(f'{self.title}{timezone.now()}'.encode('utf-8')).hexdigest()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
