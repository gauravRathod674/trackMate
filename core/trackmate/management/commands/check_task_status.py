from django.core.management.base import BaseCommand
from celery.result import AsyncResult


class Command(BaseCommand):
    help = "Check the status of a Celery task"

    def handle(self, *args, **options):
        task_id = (
            "55b758ba-d074-44a8-b929-6441a3f836da"  # Replace with the actual task ID
        )

        result = AsyncResult(task_id)

        if result.ready():
            task_result = result.result
            self.stdout.write(self.style.SUCCESS(f"Task result: {task_result}"))
        else:
            self.stdout.write(self.style.WARNING("Task is still pending..."))
