from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework import status
from rest_framework import permissions
from rest_framework.response import Response
from .serializers import*

class CustomerDeatilsView(APIView):
    serializer_class = CustomerDeatilsSerializer

    def post(self, request, *args, **kwargs):
        serializers = CustomerDeatilsSerializer(data=request.data)
        if serializers.is_valid():
            data={
                "OTP":1234
            }
            return Response(data=data, status=status.HTTP_200_OK)
        else:
            return Response(data=serializers.errors, status=status.HTTP_400_BAD_REQUEST)


class OPTView(APIView):
    serializer_class = OTPSerializer

    def post(self, request, *args, **kwargs):
        serializers = OTPSerializer(data=request.data)
        if serializers.is_valid():
            if serializers.data.get('OTP') == '1234':
                data={
                    "message":'Success'
                }
            else:
                data={
                    "message":'Invalide OTP'
                }

            return Response(data=data, status=status.HTTP_200_OK)
        else:
            return Response(data=serializers.errors, status=status.HTTP_400_BAD_REQUEST)
