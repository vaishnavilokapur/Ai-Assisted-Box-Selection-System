from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.order_create_view, name='order_create'),
    path('<int:order_id>/recommendation/', views.order_recommendation_view, name='order_recommendation'),
    path('', views.order_list_view, name='order_list'),
]

