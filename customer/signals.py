from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver

from .models import Customer, OrderModel


@receiver(user_logged_in)
def merge_guest_cart(sender, request, user, **kwargs):
    """Hand the anonymous device-cookie cart over to the account that just
    signed in, so checking out to place an order doesn't wipe out whatever
    was added to the cart before the customer logged in."""
    device = request.COOKIES.get('device')
    if not device:
        return

    guest_customer = Customer.objects.filter(device=device, user__isnull=True).first()
    if not guest_customer:
        return

    guest_order = OrderModel.objects.filter(customer=guest_customer, is_completed=False).first()
    if not guest_order or not guest_order.orderitem_set.exists():
        return

    user_customer, _ = Customer.objects.get_or_create(
        user=user, defaults={'name': user.get_username()}
    )

    OrderModel.objects.filter(
        customer=user_customer, is_completed=False
    ).exclude(pk=guest_order.pk).delete()

    guest_order.customer = user_customer
    guest_order.save(update_fields=['customer'])
    guest_order.orderitem_set.update(customer=user_customer)
