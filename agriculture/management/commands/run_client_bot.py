from django.core.management.base import BaseCommand

from client_bot.bot import main


class Command(BaseCommand):
    help = "Run the Telegram client bot for devices"

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Starting client bot..."))
        main()
