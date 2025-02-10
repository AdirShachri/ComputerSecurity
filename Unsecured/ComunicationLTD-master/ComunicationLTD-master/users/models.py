from typing import Iterable, Optional
from django.db import models

from django.contrib.auth.models import User
from django.db import models
from django.utils.timezone import now
from django.contrib.auth.hashers import check_password


class Customer(models.Model):
    name = models.CharField(max_length=150)
    email = models.CharField(max_length=150)
    phone = models.CharField(max_length=150, unique=True)
    REQUIRED_FIELDS = ['name', 'email', 'phone']
    class Meta:
        verbose_name_plural = 'Customers'

    def __str__(self):
        return self.name
    

class ResetPasswordToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=40, unique=True)  
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.token}"



    
class PasswordHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='password_history')
    password = models.CharField(max_length=128) 
    created_at = models.DateTimeField(default=now)
    created_at = models.DateTimeField(auto_now_add=True)  

    @staticmethod
    def is_recent_password(user, new_password):
       
        recent_passwords = PasswordHistory.objects.filter(user=user).order_by('-created_at')[:3]
        return any(check_password(new_password, entry.password) for entry in recent_passwords)


from django.contrib.auth.models import User
from django.db import models
from django.utils.timezone import now
from django.core.mail import send_mail
from django.conf import settings

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    failed_login_attempts = models.IntegerField(default=0) 
    lock_until = models.DateTimeField(null=True, blank=True)  

    def is_locked(self):
        return self.lock_until and now() < self.lock_until

    def send_lock_email(self):
        
        subject = "Your account has been locked"
        message = f"""
        Dear {self.user.username},

        Your account has been locked due to too many failed login attempts.
        Please try again after 2 minutes or contact support.

        Thank you,
        Support Team
        """
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [self.user.email],
            fail_silently=False,
        )

