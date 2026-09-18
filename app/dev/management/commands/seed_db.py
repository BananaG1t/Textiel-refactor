from django.contrib.auth.models import Permission
from django.core.management.base import BaseCommand
from django.contrib.contenttypes.models import ContentType

from products.models import Product
from authorization.models import Role
from users.models import User


class Command(BaseCommand):
    help = "Seed the database with development data."

    def handle(self, *args, **options):
        self.stdout.write("Seeding database...")

        self.seed_roles()
        self.seed_users()
        self.seed_stores()
        self.seed_products()

        self.stdout.write(
            self.style.SUCCESS("Database seeded successfully.")
        )

    def seed_roles(self):
        roles = [
            ("Admin", 100),
            ("Staff", 99),
            ("Employee", 1),
            ("Store Manager", 1),
            ("Store Employee", 0),
        ]

        for role_name, role_level in roles:
            Role.objects.get_or_create(name=role_name, defaults={'level': role_level})

        for role in ["Admin", "Staff"]:
            role_obj = Role.objects.get(name=role)
            role_obj.permissions.set(Permission.objects.all())

        self.stdout.write(self.style.SUCCESS("  Created roles."))

    def seed_stores(self):
        # Create development stores here.
        pass

    def seed_users(self):
        User.objects.create_user(
            email="admin@example.com",
            password="admin",
            role="Admin",
            first_name="Dev",
            last_name="Admin",
        )

        User.objects.create_user(
            email="staff@example.com",
            password="admin",
            role="Staff",
            first_name="Dev",
            last_name="Staff",
        )

        User.objects.create_user(
            email="employee@example.com",
            password="admin",
            role="Employee",
            first_name="Dev",
            last_name="Employee",
        )

        self.stdout.write(self.style.SUCCESS("  Created users."))

    def seed_products(self):
        # Create development products here.
        pass