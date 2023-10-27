from rest_framework import serializers
from mainapp.models import*
from django.contrib.auth.forms import UserCreationForm

class CustomerDeatilsSerializer(serializers.Serializer):
    name = serializers.CharField()
    age = serializers.IntegerField()
    gender = serializers.CharField()
    phone_number = serializers.IntegerField()

class OTPSerializer(serializers.Serializer):
    OTP = serializers.CharField()