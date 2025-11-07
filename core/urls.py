from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),  # Home / Dashboard
    path('about/', views.about, name='about'),
    path('pages/', views.pages_list, name='pages_list'),
    path('pages/<int:pk>/', views.pages_detail, name='pages_detail'),
    path('pages/create/', views.pages_create, name='pages_create'),
    path('pages/<int:pk>/edit/', views.pages_edit, name='pages_edit'),
    path('pages/<int:pk>/delete/', views.pages_delete, name='pages_delete'),
    path('contact/', views.contact_view, name='contact'),
]
