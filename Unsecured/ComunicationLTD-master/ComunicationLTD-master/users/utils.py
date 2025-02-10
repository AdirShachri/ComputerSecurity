from django.contrib.auth.hashers import make_password
from .models import PasswordHistory
from django.contrib.auth.hashers import check_password
from .models import PasswordHistory

def save_new_password(user, new_password):
    hashed_password = make_password(new_password)  
    PasswordHistory.objects.create(user=user, password=hashed_password)  
    print("Password saved successfully!")

def is_password_valid(user, new_password):
    for history in PasswordHistory.objects.filter(user=user):
        if check_password(new_password, history.password):  
            return False  
    return True