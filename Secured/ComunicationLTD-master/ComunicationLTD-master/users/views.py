from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.views import (
    LoginView,
    PasswordResetView,
    PasswordChangeView
)
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.db import connections
from django.conf import settings
from django.utils.timezone import now
from django.views import View
from django.contrib.messages.views import SuccessMessageMixin
from datetime import timedelta
import hashlib
import random
import string
from .forms import (
    RegisterForm, 
    LoginForm, 
    RegisterCustomerForm,
    ForgotPasswordForm,
    ResetPasswordForm
)

from .models import Customer, ResetPasswordToken
from .utils import save_new_password, is_password_valid
from django.core.mail import send_mail


def home(request):
    return render(request, 'users/home.html')


class RegisterView(View):
    form_class = RegisterForm
    template_name = 'users/register.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(to='/')  
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data.get('first_name')
            if settings.SQLI: #Protection against SQL Injection
                with connections['default'].cursor() as cursor:
                    cursor.execute("SELECT * FROM auth_user WHERE first_name=%s", [first_name])
                    print(cursor.fetchall())
            else:
                form.save()

            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}')
            return redirect(to='login')

        return render(request, self.template_name, {'form': form})
    

class CustomLoginView(LoginView):
    template_name = 'users/login.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('/')  
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        username = request.POST.get('username')
        password = request.POST.get('password')
        if settings.SQLI: #Protection against SQL Injection
            with connections['default'].cursor() as cursor:
                cursor.execute("SELECT * FROM auth_user WHERE username=%s", [username])
                print(cursor.fetchall())

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            messages.error(request, "Invalid username or password.")
            return self.render_to_response(self.get_context_data())

        
        if hasattr(user, 'profile') and user.profile.is_locked():
            messages.error(request, "Your account is locked. Try again later.")
            return self.render_to_response(self.get_context_data())

        
        user_authenticated = authenticate(request, username=username, password=password)
        if user_authenticated is not None:
            login(request, user_authenticated)
            if hasattr(user, 'profile'):
                user.profile.failed_login_attempts = 0  
                user.profile.save()
            return redirect('/')
        else:
           
            if hasattr(user, 'profile'):
                user.profile.failed_login_attempts += 1
                if user.profile.failed_login_attempts >= 3:
                    user.profile.lock_until = now() + timedelta(minutes=2) #Lock for 2 minutes
                    user.profile.save()
                    user.profile.send_lock_email()  
                    messages.error(request, "Too many failed attempts. Your account is locked for 2 minutes.")
                else:
                    messages.error(request, "Invalid username or password.")
                user.profile.save()
            else:
                messages.error(request, "Invalid username or password.")

            return self.render_to_response(self.get_context_data())

        

class RegisterCustomerView(View):
    form_class = RegisterCustomerForm
    template_name = 'users/registerCustomer.html'

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            name = form.cleaned_data.get('name')
            email = form.cleaned_data.get('email')
            phone = form.cleaned_data.get('phone')
            customer = Customer(name=name, email=email, phone=phone)

            if settings.SQLI:
                with connections['default'].cursor() as cursor:
                    cursor.execute("SELECT * FROM users_customer WHERE name=%s", [name])
                    print(cursor.fetchall())
            else:
                customer.save(using='default')

            messages.success(request, f'Account created for {name}')
            return redirect('users-home')

        return render(request, self.template_name, {'form': form})




def customer_list(request):
    customers = Customer.objects.all()
    return render(request, 'users/customer_list.html', {'customers': customers})


        
class ChangePasswordView(SuccessMessageMixin, PasswordChangeView):
    template_name = 'users/change_password.html'
    success_message = "Your password was changed successfully."
    success_url = reverse_lazy('users-home')

    def form_valid(self, form):
        new_password = form.cleaned_data.get('new_password1')
        user = self.request.user

        #check if the new password is not one of the last 3 passwords
        if not is_password_valid(user, new_password):
            messages.error(self.request, "You cannot reuse one of your last 3 passwords.")
            return render(self.request, self.template_name, {'form': form})

        
        save_new_password(user, new_password)

        return super().form_valid(form)



class ResetPasswordView(SuccessMessageMixin, PasswordResetView):
    template_name = 'users/password_reset.html'
    email_template_name = 'users/password_reset_email.html'
    subject_template_name = 'users/password_reset_subject'
    success_message = (
        "We've emailed you instructions for setting your password, "
        "if an account exists with the email you entered."
    )
    success_url = reverse_lazy('users-home')

    


def forgot_password_view(request):
    
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            
            
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                
                return render(request, 'users/forgot_password.html', {
                    'form': form,
                    'error': "User does not exist in the system"
                })
            
            #SHA-1 token
            random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
            token_sha1 = hashlib.sha1(random_string.encode('utf-8')).hexdigest()
            
            
            ResetPasswordToken.objects.create(user=user, token=token_sha1)
            
            
            subject = "Password Reset Code"
            message = f"""Hello {user.username},
You have received a password reset code: {token_sha1}
Please visit the following link to continue the process and enter the code there:
http://127.0.0.1:8000/reset_password/

Thank you,
"""
            

            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
            
            
            return render(request, 'users/forgot_password_done.html')
    else:
        form = ForgotPasswordForm()
        
    return render(request, 'users/forgot_password.html', {'form': form})




def reset_password_view(request):
    
    if request.method == 'POST':
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            token = form.cleaned_data.get('token')
            new_password = form.cleaned_data.get('new_password')
            
           
            try:
                reset_token = ResetPasswordToken.objects.get(token=token)
            except ResetPasswordToken.DoesNotExist:
                return render(request, 'users/reset_password.html', {
                    'form': form,
                    'error': "The reset code is invalid or does not exist."
                })
            
            user = reset_token.user

           
            if not is_password_valid(user, new_password):
                messages.error(request, "You cannot reuse one of your last 3 passwords.")
                return render(request, 'users/reset_password.html', {'form': form})

            
            save_new_password(user, new_password)
            
            
            user.set_password(new_password)
            user.save()
            
            
            reset_token.delete()
            
            
            messages.success(request, "Your password has been reset successfully!")
            return redirect('login')
        else:
            
            return render(request, 'users/reset_password.html', {'form': form})
    else:
        form = ResetPasswordForm()
        
    return render(request, 'users/reset_password.html', {'form': form})



