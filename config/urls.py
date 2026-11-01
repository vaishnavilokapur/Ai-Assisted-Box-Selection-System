"""
URL configuration for config project.

PackWise – AI-Assisted Smart Box Selection System.
"""
from django.contrib import admin
from django.urls import include, path
from orders.views import dashboard_home_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', dashboard_home_view, name='home'),
    path('products/', include('products.urls')),
    path('boxes/', include('boxes.urls')),
    path('orders/', include('orders.urls')),
]
