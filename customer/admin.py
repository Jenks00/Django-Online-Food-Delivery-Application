from django.contrib import admin

from .models import MenuItem, OrderModel, OrderItem, Customer


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(OrderModel)
class OrderModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'status', 'is_completed', 'created_on', 'get_cart_total')
    list_filter = ('status', 'is_completed')
    inlines = [OrderItemInline]


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'price')


admin.site.register(OrderItem)
admin.site.register(Customer)
