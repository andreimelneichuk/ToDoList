from celery import shared_task
from django.utils.timezone import now
from .models import Task

@shared_task
def send_due_date_notifications():
    tasks = Task.objects.filter(due_date__lte=now(), is_completed=False)
    for task in tasks:
        print(f"Уведомление для задачи {task.title} с истекшим сроком выполнения.")