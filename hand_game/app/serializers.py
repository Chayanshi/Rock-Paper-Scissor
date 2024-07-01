from rest_framework import serializers
from .models import *
from django.utils import timezone

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User_model
        fields = '__all__'
        
class GetUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User_model
        fields = ['id', 'email', 'firstname', 'lastname','phone', 'role', 'is_block','avatar']

