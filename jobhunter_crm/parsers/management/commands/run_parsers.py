"""Management command to run all parsers."""

from django.core.management.base import BaseCommand
from parsers.engine import run_all_parsers


class Command(BaseCommand):
    help = 'Run all vacancy parsers'

    def handle(self, *args, **options):
        result = run_all_parsers()
        self.stdout.write(
            f"Parser run complete: {result['total_new']} new, "
            f"{result['total_errors']} errors"
        )
