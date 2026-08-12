from .models import Customer, OrderModel


def cart(request):
    """Cart item count for the header badge, available on every page."""
    if request.user.is_authenticated:
        customer = Customer.objects.filter(user=request.user).first()
    else:
        device = request.COOKIES.get('device')
        customer = Customer.objects.filter(device=device).first() if device else None

    if not customer:
        return {'cart_count': 0}

    ordermodel = OrderModel.objects.filter(customer=customer, is_completed=False).first()
    return {'cart_count': ordermodel.get_cart_items if ordermodel else 0}
