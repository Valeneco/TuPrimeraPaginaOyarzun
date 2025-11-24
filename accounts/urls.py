from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),

    # Profile
    path('profile/', views.profile_view, name='profile'),
    
    # ⚡ SEPARATED EDIT VIEWS
    # 1. Update personal data
    path('profile/edit/', views.edit_profile_view, name='edit_profile'),
    
    # 2. Change password
    path('profile/password/', views.change_password_view, name='change_password'),
]