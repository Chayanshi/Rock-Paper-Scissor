from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin,BaseUserManager
# Create your models here.


class CustomUserManager(BaseUserManager):
    def _create_user(self,email,password,**extra_fields):
        if not email:
            raise ValueError("Please enter an email address")
        email = self.normalize_email(email)
        user=self.model(email=email,**extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self,email=None,password=None,**extra_fields):
         extra_fields.setdefault('is_staff',False)
         extra_fields.setdefault('is_superuser',False)
         return self._create_user(email,password,**extra_fields)

    def create_superuser(self,email=None,password=None,**extra_fields):
         extra_fields.setdefault('is_staff',True)
         extra_fields.setdefault('is_superuser',True)
         return self._create_user(email,password,**extra_fields)

class User_model(AbstractBaseUser,PermissionsMixin):
    User_Role=(
        ('Admin','admin'),
        ('Player','player')
    )
    username = models.CharField(max_length = 255)
    email = models.CharField(max_length = 255,unique = True)
    password = models.CharField(max_length = 255)
    avatar = models.ImageField(upload_to="user_avatar",null=True,blank=True)
    role = models.CharField(max_length=30,choices=User_Role)
    
    is_active=models.BooleanField(default=True)
    is_superuser=models.BooleanField(default=False)
    is_staff=models.BooleanField(default=False)
    is_block = models.BooleanField(default=False)
    otp = models.IntegerField(blank=True,null=True)
    account_verifed = models.BooleanField(default = False)
    otp_created_at = models.DateTimeField(blank=True,null=True)
    otp_verified = models.BooleanField(default=False)

    objects=CustomUserManager()

    USERNAME_FIELD='email'
    REQUIRED_FIELDS=[]

    def str(self):
        return f"{self.username} - {self.email}: account verifed {self.account_verifed}"
                                  
class room_model(models.Model):
    room_number = models.IntegerField(unique = True)
    user1_score = models.IntegerField(default = 0)
    user2_score = models.IntegerField(default = 0)
    user1 = models.ForeignKey(User_model,on_delete=models.CASCADE,related_name = "user1_model")
    user2 = models.ForeignKey(User_model,on_delete=models.CASCADE,related_name = "user2_model")
    tie_score = models.IntegerField(default = 0,null = True)
    moves = models.IntegerField(default=10)

    def str(self):
        return f"{self.room_number}"

