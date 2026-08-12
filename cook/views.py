from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.timezone import datetime
from django.views import View
from customer.models import OrderModel


class StaffDashboardMixin(UserPassesTestMixin):
    def test_func(self):
        user = self.request.user
        return user.is_staff or user.groups.filter(name='staff').exists()


class StaffRedirect(LoginRequiredMixin, View):
    """Send a signed-in staff member straight to their dashboard, or let
    them pick when they hold access to more than one of the kitchen,
    dispatch, and menu dashboards."""

    def get(self, request, *args, **kwargs):
        user = request.user
        access = {
            'cook': user.is_staff or user.groups.filter(name='staff').exists(),
            'dispatch': user.is_staff or user.groups.filter(name='dispatch').exists(),
            'menuadmin': user.is_staff or user.groups.filter(name='menu').exists(),
        }
        granted = [role for role, allowed in access.items() if allowed]

        if len(granted) > 1:
            return render(request, 'account/dashboard_picker.html', {'access': access})
        if 'cook' in granted:
            return redirect('dashboard')
        if 'dispatch' in granted:
            return redirect('dashboard2')
        if 'menuadmin' in granted:
            return redirect('menuadmin_dashboard')
        return redirect('nav')


class Dashboard(LoginRequiredMixin, StaffDashboardMixin, View):
    """Kitchen kanban board: New -> Cooking -> Ready for pickup."""

    def get(self, request, *args, **kwargs):
        today = datetime.today()
        orders = OrderModel.objects.filter(
            is_completed=True,
            created_on__year=today.year,
            created_on__month=today.month,
            created_on__day=today.day,
        )

        new_orders = orders.filter(status=OrderModel.STATUS_PLACED)
        cooking_orders = orders.filter(status=OrderModel.STATUS_COOKING)
        ready_orders = orders.filter(status=OrderModel.STATUS_READY)

        total_revenue = sum((order.get_cart_total for order in orders), 0)

        context = {
            'new_orders': new_orders,
            'cooking_orders': cooking_orders,
            'ready_orders': ready_orders,
            'total_revenue': total_revenue,
            'total_orders': orders.count(),
        }

        return render(request, 'cook/dashboard.html', context)


class OrderDetails(LoginRequiredMixin, StaffDashboardMixin, View):
    def get(self, request, pk, *args, **kwargs):
        order = get_object_or_404(OrderModel, pk=pk)
        context = {
            'price': order.get_cart_total,
            'order': order,
        }
        return render(request, 'cook/order_details.html', context)

    def post(self, request, pk, *args, **kwargs):
        order = get_object_or_404(OrderModel, pk=pk)
        if order.status in (OrderModel.STATUS_PLACED, OrderModel.STATUS_COOKING):
            order.advance_status()
        return redirect('dashboard')


def logout(request):
    return render(request, 'account/logout.html')
