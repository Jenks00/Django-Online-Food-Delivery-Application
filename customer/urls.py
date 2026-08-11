from django.urls import path
from .views import product, Remove

urlpatterns = [
    path('product/<str:pk>/', product, name='product'),
    path('remove/<str:pk>/', Remove, name='remove'),
]
