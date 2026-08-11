"""Food_delivery URL Configuration"""
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from customer.views import Home, About, Order, OrderConfirmation, Ord, Menu, MenuSearch


urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('cook/', include('cook.urls')),
    path('customer/', include('customer.urls')),
    path('dispatch/', include('dispatch.urls')),
    path('', Home.as_view(), name='nav'),
    path('about/', About.as_view(), name='about'),
    path('menu/', Menu.as_view(), name='menu'),
    path('menu/search/', MenuSearch.as_view(), name='menu-search'),
    path('order/', Order.as_view(), name='order'),
    path('cart/', Ord.as_view(), name='cart'),
    path('order_confirmation/', OrderConfirmation.as_view(), name='order_confirmation'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
