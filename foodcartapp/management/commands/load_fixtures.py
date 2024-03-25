from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Load fixtures"

    def handle(self, *args, **options):
        call_command("makemigrations")
        call_command("migrate")
        call_command("loaddata",
                     "db_restaurants_fixture.json")
        call_command("loaddata",
                     "db_productcategory_fixture.json")
        call_command("loaddata",
                     "db_product_fixture.json")
        call_command("loaddata",
                     "db_restaurantmenuitem_fixture.json")
        call_command("loaddata",
                     "db_auth_user_fixture.json")
