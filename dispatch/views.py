from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.timezone import datetime
from django.views import View
from customer.models import OrderModel


class DispatchDashboardMixin(UserPassesTestMixin):
    def test_func(self):
        user = self.request.user
        return user.is_staff or user.groups.filter(name='dispatch').exists()


class Dashboard(LoginRequiredMixin, DispatchDashboardMixin, View):
    """Delivery kanban board: Ready for pickup -> Out for delivery -> Delivered."""

    def get(self, request, *args, **kwargs):
        today = datetime.today()
        orders = OrderModel.objects.filter(
            is_completed=True,
            created_on__year=today.year,
            created_on__month=today.month,
            created_on__day=today.day,
        )

        ready_orders = orders.filter(status=OrderModel.STATUS_READY)
        out_for_delivery_orders = orders.filter(status=OrderModel.STATUS_OUT_FOR_DELIVERY)
        delivered_orders = orders.filter(status=OrderModel.STATUS_DELIVERED)

        total_revenue = sum((order.get_cart_total for order in orders), 0)

        context = {
            'ready_orders': ready_orders,
            'out_for_delivery_orders': out_for_delivery_orders,
            'delivered_orders': delivered_orders,
            'total_revenue': total_revenue,
            'total_orders': orders.count(),
        }

        return render(request, 'dispatch/dashboard2.html', context)


class OrderDetails(LoginRequiredMixin, DispatchDashboardMixin, View):
    def get(self, request, pk, *args, **kwargs):
        order = get_object_or_404(OrderModel, pk=pk)
        context = {
            'price': order.get_cart_total,
            'order': order,
        }
        return render(request, 'dispatch/shipped_details.html', context)

    def post(self, request, pk, *args, **kwargs):
        order = get_object_or_404(OrderModel, pk=pk)
        if order.status in (OrderModel.STATUS_READY, OrderModel.STATUS_OUT_FOR_DELIVERY):
            order.advance_status()
        return redirect('dashboard2')


def logout(request):
    return render(request, 'account/logout.html')
