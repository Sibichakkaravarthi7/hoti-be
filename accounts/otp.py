import datetime
import django.utils as django_utils
from time import strftime

from rest_framework import generics
from django.utils import timezone

from django.shortcuts import render
from django.core.mail import send_mail
import math, random
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import EmailOTP, User
from .send_mail import send_email
from .serializers import ForgetPasswordSerializer,EmailResetSerializer
from .utils import check_email_exists


def home(request):
    return render(request, "home.html")


def generateOTP():
    digits = "0123456789"
    OTP = ""
    for i in range(4):
        OTP += digits[math.floor(random.random() * 10)]
    return OTP


def send_otp_mail(recipient):
    o = generateOTP()
    body = '<p>Your Hoti OTP is <strong>' + o + '</strong></p>'
    # send_mail('OTP request', o, '<your gmail id>', [email], fail_silently=False, html_message=htmlgen)
    sender = 'hotimanage@gmail.com'  # Replace with your sender email address
    recipient = recipient  # Replace with the recipient email address
    subject = 'OTP From HOTI'

    is_sent = send_email(sender, recipient, subject, body)

    return is_sent,o

class SendOTP(APIView):
    def post(self, request):
        input_data = request.data
        recipient = input_data.get("email",'')
        email_registered = check_email_exists(recipient)
        if email_registered:
            return Response({"msg": 'This email already used by another user'}, status=status.HTTP_403_FORBIDDEN)

        is_sent,otp = send_otp_mail(recipient)
        # if not is_sent:
        #     is_sent = send_email(sender, 'hotimanage@gmail.com' , subject, body)
        otp_obj = EmailOTP(otp=otp,email=recipient)
        otp_obj.save()
        return Response({"msg": 'OTP sent successfully! Please check you email'}, status=status.HTTP_202_ACCEPTED)



class VerifyOTP(APIView):
    def post(self, request):
        input_data = request.data
        otp = input_data.get("otp", '')
        email = input_data.get("email", '')
        five_minutes_ago = timezone.now() + datetime.timedelta(minutes=-5)
        # latest_records = EmailOTP.objects.filter(created_at__gte=five_minutes_ago)
        # em = EmailOTP.objects.filter(otp=2345, user__email='ramesh.ponnusami.1995@gmail.com'             )

        try:
            email_otp_obj = EmailOTP.objects.get(otp=otp, email=email)
            return Response({"msg": 'OTP Verified Successfully!'}, status=status.HTTP_202_ACCEPTED)
        except EmailOTP.DoesNotExist:
            email_otp_obj = None
            return Response({"msg": 'Please enter valid OTP'}, status=status.HTTP_403_FORBIDDEN)


class VerifyEmailAndSendOTP(APIView):
    def post(self, request):
        input_data = request.data
        recipient = input_data.get("email",'')
        email_registered = check_email_exists(recipient)
        if email_registered:
            is_sent,otp = send_otp_mail(recipient)
            # if not is_sent:
            #     is_sent = send_email(sender, 'hotimanage@gmail.com' , subject, body)
            otp_obj = EmailOTP(otp=otp,user=email_registered,email=recipient)
            otp_obj.save()
            return Response({"msg": 'OTP sent successfully! Please check you email'}, status=status.HTTP_202_ACCEPTED)
        else:
            return Response({"otp": None, 'msg': "Please submit registered email"}, status=status.HTTP_403_FORBIDDEN)
        
class VerifyAndChangeEmail(APIView):
    serializer_class=EmailResetSerializer
    def post(self,request):
        input_data=request.data
        serializer=self.serializer_class(data=input_data)
        if serializer.is_valid():
            email=input_data.get("email", '')
            otp=input_data.get("otp",'')
            new_email=input_data.get("new_email",'')

            try:
                email_otp_obj = EmailOTP.objects.get(otp=otp, email=email)
            except EmailOTP.DoesNotExist:
                email_otp_obj = None
                return Response({"msg": 'Please enter valid OTP'}, status=status.HTTP_403_FORBIDDEN)
            
            try:
                user_obj = User.objects.get(email=email)
                user_obj.email=new_email
                user_obj.save()
                return Response({"msg": 'Email Changed Successfully'}, status=status.HTTP_202_ACCEPTED)
            except User.DoesNotExist:
                user_obj = None
                return Response({"msg": 'Registered mail doesnt exists'}, status=status.HTTP_403_FORBIDDEN)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyOTPAndChangePassword(APIView):
    """
        An endpoint for reset forget password.
        """
    serializer_class = ForgetPasswordSerializer
    def post(self, request):
        input_data = request.data
        serializer = self.serializer_class(data=input_data)

        if serializer.is_valid():
            otp = input_data.get("otp", '')
            email = input_data.get("email", '')
            new_password = input_data.get("new_password", '')
            five_minutes_ago = timezone.now() + datetime.timedelta(minutes=-5)
            # latest_records = EmailOTP.objects.filter(created_at__gte=five_minutes_ago)
            # em = EmailOTP.objects.filter(otp=2345, user__email='ramesh.ponnusami.1995@gmail.com'             )

            try:
                email_otp_obj = EmailOTP.objects.get(otp=otp, email=email)
            except EmailOTP.DoesNotExist:
                email_otp_obj = None
                return Response({"msg": 'Please enter valid OTP'}, status=status.HTTP_403_FORBIDDEN)

            try:
                user_obj = User.objects.get(email=email)
                user_obj.set_password(new_password)
                user_obj.save()
                return Response({"msg": 'Password Changed Successfully'}, status=status.HTTP_202_ACCEPTED)
            except User.DoesNotExist:
                user_obj = None
                return Response({"msg": 'Registered mail doesnt exists'}, status=status.HTTP_403_FORBIDDEN)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

