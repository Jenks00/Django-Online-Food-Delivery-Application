from django.shortcuts import render, redirect
from django.views import View
from django.db.models import Q
from .models import *


def _get_or_create_customer(request):
    """
    Returns the Customer tied to the logged-in user, falling back to an
    anonymous per-device customer identified by the `device` cookie that
    base.html sets on first visit.
    """
    if request.user.is_authenticated:
        customer, _ = Customer.objects.get_or_create(
            user=request.user,
            defaults={'name': request.user.get_username()},
        )
        return customer

    device = request.COOKIES.get('device')
    if not device:
        device = 'anonymous'
    customer, _ = Customer.objects.get_or_create(device=device)
    return customer


class Home(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'customer/nav.html')


class About(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'customer/about.html')


class Order(View):
    def get(self, request, *args, **kwargs):
        menu = MenuItem.objects.all()
        context = {
            'menu': menu,
        }
        return render(request, 'customer/order.html', context)


class Menu(View):
    def get(self, request, *args, **kwargs):
        menu_items = MenuItem.objects.all()

        context = {
            'menu_items': menu_items,
            'query': '',
        }

        return render(request, 'customer/menu.html', context)


class MenuSearch(View):
    def get(self, request, *args, **kwargs):
        query = self.request.GET.get('q', '')

        menu_items = MenuItem.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query)
        )

        context = {
            'menu_items': menu_items,
            'query': query,
        }

        return render(request, 'customer/menu.html', context)


def product(request, pk):
    product = MenuItem.objects.get(id=pk)

    if request.method == 'POST':
        customer = _get_or_create_customer(request)
        ordermodel, created = OrderModel.objects.get_or_create(
            customer=customer,
            is_completed=False,
        )
        order_item, created = OrderItem.objects.get_or_create(
            customer=customer, ordermodel=ordermodel, menuItem=product
        )
        quantity = request.POST.get('quantity') or 1
        order_item.quantity = quantity
        order_item.save()
        return redirect('cart')

    context = {'product': product}
    return render(request, 'customer/product.html', context)


def Remove(request, pk):
    OrderItem.objects.filter(id=pk).delete()
    return redirect('cart')


class Ord(View):
    template_name = 'customer/cart.html'

    def get(self, request, *args, **kwargs):
        customer = _get_or_create_customer(request)
        ordermodel, created = OrderModel.objects.get_or_create(customer=customer, is_completed=False)

        context = {
            'order': ordermodel,
        }

        return render(request, 'customer/cart.html', context)

    def post(self, request, *args, **kwargs):
        customer = _get_or_create_customer(request)

        name = request.POST.get('name')
        email = request.POST.get('email')
        address = request.POST.get('address')
        phone_no = request.POST.get('phone_no') or 0

        ordermodel, created = OrderModel.objects.get_or_create(customer=customer, is_completed=False)
        ordermodel.name = name
        ordermodel.email = email
        ordermodel.address = address
        ordermodel.phone_no = phone_no
        ordermodel.is_completed = True
        ordermodel.status = OrderModel.STATUS_PLACED
        ordermodel.save()

        context = {
            'order': ordermodel,
        }

        return render(request, 'customer/order_confirmation.html', context)


class OrderConfirmation(View):
    def get(self, request, *args, **kwargs):
        customer = _get_or_create_customer(request)

        ordermodel = OrderModel.objects.filter(customer=customer, is_completed=True).first()
        if ordermodel is None:
            return redirect('menu')

        context = {
            'order': ordermodel,
        }

        return render(request, 'customer/order_confirmation.html', context)
