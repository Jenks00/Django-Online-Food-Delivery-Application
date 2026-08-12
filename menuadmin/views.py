from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View

from customer.models import MenuItem
from .forms import MenuItemForm


class MenuAdminMixin(UserPassesTestMixin):
    def test_func(self):
        user = self.request.user
        return user.is_staff or user.groups.filter(name='menu').exists()


class Dashboard(LoginRequiredMixin, MenuAdminMixin, View):
    def get(self, request, *args, **kwargs):
        context = {'menu_items': MenuItem.objects.all()}
        return render(request, 'menuadmin/dashboard.html', context)


class ItemCreate(LoginRequiredMixin, MenuAdminMixin, View):
    def get(self, request, *args, **kwargs):
        context = {'form': MenuItemForm(), 'is_new': True}
        return render(request, 'menuadmin/item_form.html', context)

    def post(self, request, *args, **kwargs):
        form = MenuItemForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('menuadmin_dashboard')
        return render(request, 'menuadmin/item_form.html', {'form': form, 'is_new': True})


class ItemUpdate(LoginRequiredMixin, MenuAdminMixin, View):
    def get(self, request, pk, *args, **kwargs):
        item = get_object_or_404(MenuItem, pk=pk)
        context = {'form': MenuItemForm(instance=item), 'item': item, 'is_new': False}
        return render(request, 'menuadmin/item_form.html', context)

    def post(self, request, pk, *args, **kwargs):
        item = get_object_or_404(MenuItem, pk=pk)
        form = MenuItemForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            form.save()
            return redirect('menuadmin_dashboard')
        return render(request, 'menuadmin/item_form.html', {'form': form, 'item': item, 'is_new': False})


class ItemDelete(LoginRequiredMixin, MenuAdminMixin, View):
    def post(self, request, pk, *args, **kwargs):
        get_object_or_404(MenuItem, pk=pk).delete()
        return redirect('menuadmin_dashboard')
