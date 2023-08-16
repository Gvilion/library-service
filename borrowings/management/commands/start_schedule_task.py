from django.core.management import BaseCommand
from django_q.models import Schedule


class Command(BaseCommand):
    help = "Start sending notifications to tg chat about borrowings"

    def handle(self, *args, **options):

        Schedule.objects.create(
            func='borrowings.tasks.get_overdue_borrowings',
            repeats=-1,
            schedule_type=Schedule.DAILY,
        )
        self.stdout.write(
            self.style.SUCCESS('Successfully started')
        )