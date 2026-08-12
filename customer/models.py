from decimal import Decimal

from django.db import models
from django.contrib.auth.models import User


class Customer(models.Model):
    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, null=True, blank=True)
    email = models.CharField(max_length=200, null=True, blank=True)
    device = models.CharField(max_length=200, null=True, blank=True)
    phone = models.CharField(max_length=32, null=True, blank=True, unique=True)
    phone_verified = models.BooleanField(default=False)

    def __str__(self):
        if self.name:
            name = self.name
        else:
            name = self.device
        return str(name)


class MenuItem(models.Model):
    name = models.CharField(null=False, blank=False, max_length=100)
    description = models.TextField(null=False, blank=False)
    image = models.ImageField(upload_to='menu_images/')
    price = models.DecimalField(null=True, blank=True, max_digits=7, decimal_places=2)

    def __str__(self):
        return self.name


class OrderModel(models.Model):
    """
    An order moves through a single pipeline once the customer checks out:

        placed -> cooking -> ready -> out_for_delivery -> delivered

    The cook dashboard owns the placed/cooking/ready transitions, the
    dispatch dashboard owns ready/out_for_delivery/delivered.
    """
    STATUS_PLACED = 'placed'
    STATUS_COOKING = 'cooking'
    STATUS_READY = 'ready'
    STATUS_OUT_FOR_DELIVERY = 'out_for_delivery'
    STATUS_DELIVERED = 'delivered'

    STATUS_CHOICES = [
        (STATUS_PLACED, 'New'),
        (STATUS_COOKING, 'Cooking'),
        (STATUS_READY, 'Ready for pickup'),
        (STATUS_OUT_FOR_DELIVERY, 'Out for delivery'),
        (STATUS_DELIVERED, 'Delivered'),
    ]

    # Maps a status to the status it advances to when a staff member
    # completes their step. Terminal status (delivered) has no entry.
    NEXT_STATUS = {
        STATUS_PLACED: STATUS_COOKING,
        STATUS_COOKING: STATUS_READY,
        STATUS_READY: STATUS_OUT_FOR_DELIVERY,
        STATUS_OUT_FOR_DELIVERY: STATUS_DELIVERED,
    }

    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=50, null=True, blank=True)
    email = models.CharField(max_length=50, null=True, blank=True)
    address = models.CharField(max_length=50, null=True, blank=True)
    phone_no = models.PositiveIntegerField(default=0, null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PLACED)

    class Meta:
        ordering = ['-created_on']

    def __str__(self):
        return f'Order: {self.created_on.strftime("%b %d %I:%M %p")}'

    @property
    def is_shipped(self):
        """True once the kitchen has handed the order to dispatch."""
        return self.status in (
            self.STATUS_READY,
            self.STATUS_OUT_FOR_DELIVERY,
            self.STATUS_DELIVERED,
        )

    @property
    def is_delivered(self):
        return self.status == self.STATUS_DELIVERED

    @property
    def status_label(self):
        return dict(self.STATUS_CHOICES).get(self.status, self.status)

    def advance_status(self):
        """Move the order to its next pipeline status, if any."""
        next_status = self.NEXT_STATUS.get(self.status)
        if next_status:
            self.status = next_status
            self.save(update_fields=['status'])
        return self.status

    @property
    def get_cart_total(self):
        orderitems = self.orderitem_set.all()
        total = sum((item.get_total for item in orderitems), Decimal('0.00'))
        return total

    @property
    def get_cart_items(self):
        orderitems = self.orderitem_set.all()
        total = sum(item.quantity for item in orderitems)
        return total


class OrderItem(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.PositiveIntegerField(null=True, blank=True, default=1)
    menuItem = models.ForeignKey(MenuItem, on_delete=models.CASCADE, null=True, blank=True)
    ordermodel = models.ForeignKey(OrderModel, on_delete=models.CASCADE, null=True, blank=True)

    @property
    def get_total(self):
        total = self.menuItem.price * self.quantity
        return total
