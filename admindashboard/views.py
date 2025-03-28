from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


from django.db.models import F
from accounts.permissions import IsSuperUser

from accounts.models import Brand, Agency, User, VERIFIED_STATUS
from django.contrib.auth import logout

@login_required(login_url='login')
def home_view(request):
    # Perform any necessary logic here

    return render(request, 'base.html')
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)


        if user is not None:
            if user.is_superuser==True:
                login(request, user)
                return render(request, 'base.html')
            else:
                error_message = 'Invalid username or password.'
                return render(request, 'admindashboard/login.html', {'error_message': error_message})

            # Replace 'home' with your desired URL
        else:
            error_message = 'Invalid username or password.'
            return render(request, 'admindashboard/login.html', {'error_message': error_message})
    else:
        return render(request, 'admindashboard/login.html')



def logout_view(request):
    logout(request)
    return redirect('login')


def perform_action(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        print(action)
        users_obj = User.objects.filter(Q(verified_status='Unverified') | Q(verified_status__isnull=True)).update(verified_status='Verified')

        # Perform the action based on the submitted data
        # Example: Update the brand status, send notifications, etc.

        # Redirect to the brand detail page or any other desired page
        # return redirect('home', brand_id=brand_id)
        return render(request, 'base.html')


class UpdateVerifiedToALLByAPI(APIView):
    """ This API for change  the verified status to verified for all pending users"""
    permission_classes = [IsAuthenticated,IsSuperUser]

    def get(self, request):
        users_obj = User.objects.filter(Q(verified_status='Unverified') | Q(verified_status__isnull=True)).update(
            verified_status='Verified')

        return Response({"msg" : "Updated Successfully"})


from django.db.models import Value
from django.db.models.functions import Coalesce

class AdminInfluncerListView(APIView):
    permission_classes = [IsAuthenticated, IsSuperUser]

    def get_queryset(self):
        return User.objects.filter(user_type='influencer').annotate(
            status=Coalesce('verified_status', Value('Unverified'))
        ).values('first_name', 'last_name', 'email', 'date_joined', 'status', user_id=F('id'))  

    def get(self, request):
        queryset = self.get_queryset().all()
        return Response(queryset)



class AdminBrandListView(APIView):
    permission_classes = [IsAuthenticated,IsSuperUser]
    def get_queryset(self):
        return Brand.objects.filter(user__user_type='brand').values('company_name','website','user_id',
                                    location=F('user__location'),date_joined=F('user__date_joined'),
                                    verified_status=F('user__verified_status'))

    def get(self, request):
        queryset = self.get_queryset().all()
        return Response(queryset)


class AdminAgencyListView(APIView):
    permission_classes = [IsAuthenticated,IsSuperUser]

    def get_queryset(self):
        return Agency.objects.filter(user__user_type='agency').values('agency_name','website','user_id',
                                    location=F('user__location'),date_joined=F('user__date_joined'),verified_status=F('user__verified_status'))

    def get(self, request):
        queryset = self.get_queryset().all()
        return Response(queryset)


class UpdateUserVerifiedStatus(APIView):
    permission_classes = [IsAuthenticated,IsSuperUser]

    def put(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'detail': 'User not found.'}, status=404)

        # Update the verified_status

        input_verify_status = request.data.get('verify_status')
        exists = any(input_verify_status == status[0] for status in VERIFIED_STATUS)

        if not exists:
            return Response({'detail': 'VERIFIED_STATUS is not found.'}, status=404)
        user.verified_status = input_verify_status
        user.save()

        return Response({'detail': 'Verified status updated successfully.'})

class CountSummaryAPIView(APIView):
    permission_classes = [IsAuthenticated, IsSuperUser]

    def get_user_counts(self, user_type):
        verified_count = User.objects.filter(user_type=user_type, verified_status='Verified').count()
        null_count=User.objects.filter(user_type=user_type, verified_status=None).count()
        unverified_count = User.objects.filter(user_type=user_type, verified_status='UnVerified').count()
        rejected_count = User.objects.filter(user_type=user_type, verified_status='Rejected').count()
        return {
            'verified_count': verified_count,
            'unverified_count': unverified_count+null_count,
            'rejected_count': rejected_count
        }

    def get(self, request):
        influencer_count = User.objects.filter(user_type='influencer').count()
        brand_count = Brand.objects.filter(user__user_type='brand').count()
        agency_count = Agency.objects.filter(user__user_type='agency').count()

        influencer_counts = self.get_user_counts('influencer')
        brand_counts = self.get_user_counts('brand')
        agency_counts = self.get_user_counts('agency')

        summary = {
            'influencer_count': influencer_count,
            'influencer_verified_count': influencer_counts['verified_count'],
            'influencer_unverified_count': influencer_counts['unverified_count'],
            'influencer_rejected_count': influencer_counts['rejected_count'],
            'brand_count': brand_count,
            'brand_verified_count': brand_counts['verified_count'],
            'brand_unverified_count': brand_counts['unverified_count'],
            'brand_rejected_count': brand_counts['rejected_count'],
            'agency_count': agency_count,
            'agency_verified_count': agency_counts['verified_count'],
            'agency_unverified_count': agency_counts['unverified_count'],
            'agency_rejected_count': agency_counts['rejected_count'],
        }

        return Response(summary)




