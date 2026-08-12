"""
Seeds the database with a small menu and a handful of sample orders spread
across every stage of the pipeline, so a fresh checkout of this project
shows something interesting immediately instead of three empty dashboards.

    python manage.py seed_demo_data
"""
import io

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand

from customer.models import Customer, MenuItem, OrderItem, OrderModel

MENU_ITEMS = [
    ("Margherita Pizza", "Wood-fired pizza with San Marzano tomato, fresh mozzarella and basil.", 14.50, (214, 96, 47)),
    ("Truffle Mushroom Risotto", "Creamy arborio rice, wild mushrooms, shaved parmesan, black truffle oil.", 18.00, (91, 84, 76)),
    ("Grilled Salmon Bowl", "Miso-glazed salmon, sticky rice, edamame, pickled cucumber.", 21.00, (63, 125, 88)),
    ("Basil Smash Burger", "Double smash patty, aged cheddar, basil aioli, brioche bun.", 15.75, (179, 67, 47)),
    ("Roasted Vegetable Tagine", "Slow-roasted seasonal vegetables, apricot, couscous, harissa.", 16.25, (201, 138, 18)),
    ("Charred Corn Elote Salad", "Grilled corn, cotija, lime crema, chili, cilantro.", 9.50, (58, 110, 165)),
]

SAMPLE_ORDERS = [
    ("Grace Hopper", "grace@example.com", "12 Compiler Ave", 5551110001, OrderModel.STATUS_PLACED),
    ("Alan Turing", "alan@example.com", "8 Enigma St", 5551110002, OrderModel.STATUS_PLACED),
    ("Katherine Johnson", "katherine@example.com", "4 Orbit Rd", 5551110003, OrderModel.STATUS_COOKING),
    ("Margaret Hamilton", "margaret@example.com", "1 Apollo Way", 5551110004, OrderModel.STATUS_READY),
    ("Radia Perlman", "radia@example.com", "22 Spanning Tree Ln", 5551110005, OrderModel.STATUS_READY),
    ("Barbara Liskov", "barbara@example.com", "3 Substitution Ct", 5551110006, OrderModel.STATUS_OUT_FOR_DELIVERY),
    ("Hedy Lamarr", "hedy@example.com", "17 Frequency Dr", 5551110007, OrderModel.STATUS_DELIVERED),
]


def _placeholder_image(color):
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        return None
    img = Image.new("RGB", (800, 600), color=color)
    draw = ImageDraw.Draw(img)
    draw.rectangle([40, 40, 760, 560], outline=(255, 255, 255), width=6)
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG")
    return ContentFile(buffer.getvalue())


class Command(BaseCommand):
    help = "Seed a demo menu and sample orders across every pipeline stage."

    def handle(self, *args, **options):
        items = []
        for name, description, price, color in MENU_ITEMS:
            item, created = MenuItem.objects.get_or_create(
                name=name, defaults={"description": description, "price": price}
            )
            if created and not item.image:
                image = _placeholder_image(color)
                if image:
                    item.image.save(f"{name.lower().replace(' ', '_')}.jpg", image, save=True)
            items.append(item)
            self.stdout.write(self.style.SUCCESS(f"menu item: {name}"))

        for i, (name, email, address, phone, status) in enumerate(SAMPLE_ORDERS):
            customer, _ = Customer.objects.get_or_create(
                device=f"seed-device-{i}", defaults={"name": name}
            )
            order, created = OrderModel.objects.get_or_create(
                email=email,
                defaults={
                    "customer": customer,
                    "name": name,
                    "address": address,
                    "phone_no": phone,
                    "is_completed": True,
                    "status": status,
                },
            )
            if not created:
                continue
            OrderItem.objects.create(
                customer=customer, ordermodel=order, menuItem=items[i % len(items)], quantity=(i % 3) + 1
            )
            OrderItem.objects.create(
                customer=customer, ordermodel=order, menuItem=items[(i + 1) % len(items)], quantity=1
            )
            self.stdout.write(self.style.SUCCESS(f"order: {name} ({status})"))

        self.stdout.write(self.style.SUCCESS("Demo data ready."))
