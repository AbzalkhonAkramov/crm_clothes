import random
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction
from core.models import ClothesProduct, Customer, Order, OrderItem


class Command(BaseCommand):
    help = 'Generates dummy data for the CRM system'

    def handle(self, *args, **kwargs):
        self.stdout.write('Generating dummy data...')

        # Create superuser if it doesn't exist
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@example.com', 'admin')
            self.stdout.write(self.style.SUCCESS('Superuser created: admin/admin'))

        # Generate products
        self.generate_products()

        # Generate customers
        self.generate_customers()

        # Generate orders
        self.generate_orders()

        self.stdout.write(self.style.SUCCESS('Dummy data generated successfully!'))

    def generate_products(self):
        if ClothesProduct.objects.exists():
            self.stdout.write('Products already exist. Skipping...')
            return

        product_names = [
            'Classic T-Shirt', 'Slim Fit Jeans', 'Casual Hoodie', 'Summer Dress',
            'Formal Shirt', 'Winter Jacket', 'Sports Shorts', 'Elegant Blouse',
            'Comfortable Sweater', 'Stylish Skirt'
        ]

        colors = ['Red', 'Blue', 'Green', 'Black', 'White', 'Yellow', 'Purple', 'Pink', 'Gray', 'Navy']
        sizes = ['S', 'M', 'L', 'XL']

        for name in product_names:
            ClothesProduct.objects.create(
                name=name,
                description=f"This is a high-quality {name.lower()} suitable for all occasions.",
                price=round(random.uniform(19.99, 99.99), 2),
                size=random.choice(sizes),
                color=random.choice(colors),
                stock_quantity=random.randint(10, 100)
            )

        self.stdout.write(self.style.SUCCESS(f'Created {len(product_names)} products'))

    def generate_customers(self):
        if Customer.objects.exists():
            self.stdout.write('Customers already exist. Skipping...')
            return

        first_names = ['John', 'Jane', 'Michael', 'Emily', 'David']
        last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones']

        for i in range(5):
            first_name = first_names[i]
            last_name = last_names[i]

            Customer.objects.create(
                first_name=first_name,
                last_name=last_name,
                email=f"{first_name.lower()}.{last_name.lower()}@example.com",
                phone_number=f"+1 555-{random.randint(100, 999)}-{random.randint(1000, 9999)}",
                address=f"{random.randint(100, 999)} Main St, Anytown, CA {random.randint(10000, 99999)}"
            )

        self.stdout.write(self.style.SUCCESS('Created 5 customers'))

    def generate_orders(self):
        if Order.objects.exists():
            self.stdout.write('Orders already exist. Skipping...')
            return

        customers = list(Customer.objects.all())
        products = list(ClothesProduct.objects.all())
        statuses = ['Pending', 'Shipped', 'Delivered', 'Cancelled']

        with transaction.atomic():
            for i in range(10):
                # Create order
                customer = random.choice(customers)
                status = random.choice(statuses)

                order = Order.objects.create(
                    customer=customer,
                    status=status,
                    total_amount=0  # Will be updated after adding items
                )

                # Add 1-3 items to the order
                num_items = random.randint(1, 3)
                order_products = random.sample(products, num_items)

                total_amount = 0
                for product in order_products:
                    quantity = random.randint(1, 5)
                    price = product.price

                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=quantity,
                        price=price
                    )

                    total_amount += price * quantity

                # Update order total
                order.total_amount = total_amount
                order.save()

        self.stdout.write(self.style.SUCCESS('Created 10 orders with items'))