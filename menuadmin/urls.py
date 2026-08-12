from django.urls import path
from .views import Dashboard, ItemCreate, ItemUpdate, ItemDelete

urlpatterns = [
    path('dashboard3/', Dashboard.as_view(), name='menuadmin_dashboard'),
    path('new/', ItemCreate.as_view(), name='menuadmin_item_create'),
    path('<int:pk>/edit/', ItemUpdate.as_view(), name='menuadmin_item_update'),
    path('<int:pk>/delete/', ItemDelete.as_view(), name='menuadmin_item_delete'),
]
