from django.urls import path
from dispatch.views import Dashboard, OrderDetails


urlpatterns = [
    path('dashboard2/', Dashboard.as_view(), name='dashboard2'),
    path('order/<int:pk>/', OrderDetails.as_view(), name='shipped_details'),
]
