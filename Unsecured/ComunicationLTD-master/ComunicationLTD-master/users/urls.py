from django.urls import path
from django.contrib.auth import views as auth_views
from .views import (
    home,
    RegisterView,
    CustomLoginView,
    RegisterCustomerView,
    customer_list,
    ChangePasswordView,
    ResetPasswordView,           
    forgot_password_view,        
    reset_password_view          

)

urlpatterns = [
    path('', home, name='users-home'),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('customers_register',RegisterCustomerView.as_view(),name='customers_register'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('forgot_password/', forgot_password_view, name='forgot_password'),
    path('reset_password/', reset_password_view, name='reset_password'),
    path('change_password/', ChangePasswordView.as_view(), name='change_password'),
    path('reset_password_builtin/', ResetPasswordView.as_view(), name='reset-password-builtin'),
    path('forgot_password/', forgot_password_view, name='forgot_password'),
    path('reset_password/', reset_password_view, name='reset_password'),
    
]

