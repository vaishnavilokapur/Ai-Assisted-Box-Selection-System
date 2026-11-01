from django.urls import path
from . import views

urlpatterns = [
    path('', views.box_list, name='box_list'),
    path('create/', views.box_create, name='box_create'),
    path('<int:pk>/edit/', views.box_update, name='box_update'),
    path('<int:pk>/delete/', views.box_delete, name='box_delete'),
]

