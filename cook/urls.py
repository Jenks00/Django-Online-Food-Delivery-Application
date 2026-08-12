from django.urls import path
from .views import Dashboard, OrderDetails, StaffRedirect, logout


urlpatterns = [
    path('dashboard/', Dashboard.as_view(), name='dashboard'),
    path('orders/<int:pk>/', OrderDetails.as_view(), name='order_details'),
    path('accounts/logout', logout, name='accounts/logout'),
    path('staff/', StaffRedirect.as_view(), name='staff_redirect'),
]
