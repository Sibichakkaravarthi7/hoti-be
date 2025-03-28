import json
from datetime import date, timedelta
from django.db.models import Q
from django.core import serializers
from django.http import JsonResponse
from rest_framework import generics, filters, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from helpers.utils import convert_ordered_dict_to_dict
from master.models import ContentCategory
from accounts.serializers import UserSerializer, InfluencerSerializer, AgencySerializer, BrandSerializer, \
    UserFullNameMetaSerializer
from accounts.models import User, Brand, Influencer, Agency
from accounts.utils import get_user_type_serializer, user_search_fields_dict, get_user_type_serializer_explicitly, \
    get_user_custom_details_by_id, common_search_feilds
from django.db.models import F
from django.db.models import Value
from django.db.models.functions import Concat
from Mobile.serializers import DashboardProfileSearchSerializer


class mobileUserSearchMetaView(APIView):
    permission_classes = [IsAuthenticated]


    def get(self, request, user_type=None):
        queryset = User.objects.annotate(value=F('id'),label=Concat('first_name',
                                        Value(' '), 'last_name' ),type=Value('profile'))
        queryset = queryset.filter(user_type=user_type)
        search_query = self.request.query_params.get('q', None)
        search_feilds = ['first_name', 'last_name', 'username']
        if search_feilds:
            q_list = [Q(**{f'{field}__icontains': search_query}) for field in search_feilds]
            query = Q()
            for q in q_list:
                query |= q
            if search_query is not None:
                queryset = queryset.filter(query)

        user_dict = list(queryset.values('value', 'label', 'type'))
        #generate content category Meta:
        content_queryset = ContentCategory.objects.annotate(value=F('id'), label=F('content_category'),
                                              type=Value('content_category'))
        content_queryset = content_queryset.filter(
            Q(content_category__icontains=search_query)
        )
        content_dict = list(content_queryset.values('value', 'label', 'type'))
        merged_list = user_dict + content_dict


        return JsonResponse({"data":merged_list}, safe=False)


class mobileUserBrandDetailsByIdView(APIView):
    permission_classes = [IsAuthenticated]


    def get(self, request, user_id=None):

       return get_user_custom_details_by_id(user_id, Brand, BrandSerializer,user_type='brand')


class mobileUserAgencyDetailsByIdView(APIView):
    permission_classes = [IsAuthenticated]


    def get(self, request, user_id=None):
        return get_user_custom_details_by_id(user_id, Agency, AgencySerializer,user_type='agency')


class mobileUserInfluencerDetailsByIdView(APIView):
    permission_classes = [IsAuthenticated]


    def get(self, request, user_id=None):
        return get_user_custom_details_by_id(user_id, Influencer, InfluencerSerializer,user_type='influencer')


class mobileUserProfileSearchMetaView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserFullNameMetaSerializer

    def get_influencer_full_names(self, search_str):
        search_words = search_str.split()
        query = Q()
        for word in search_words:
            query &= (
                Q(first_name__icontains=word) | Q(last_name__icontains=word) | Q(username__icontains=word)
            )

        queryset = User.objects.filter(user_type='influencer').filter(query)
        full_name_list = queryset.annotate(full_name=Concat('first_name', Value(' '), 'last_name')).values('full_name')
        full_name_list = [userobj['full_name'] for userobj in full_name_list]
        return full_name_list

    def get_brand_full_names(self, search_str):
        search_words = search_str.split()
        query = Q()
        for word in search_words:
            query &= (
                Q(brand__company_name__icontains=word) | Q(brand__website__icontains=word)
            )

        queryset = User.objects.filter(user_type='brand', brand__isnull=False).filter(query)
        full_name_list = queryset.annotate(full_name=Concat('first_name', Value(' '), 'last_name')).values('full_name')
        full_name_list = [userobj['full_name'] for userobj in full_name_list]
        return full_name_list

    def get_agency_full_names(self, search_str):
        search_words = search_str.split()
        query = Q()
        for word in search_words:
            query &= (
                Q(agency__agency_name__icontains=word) | Q(agency__website__icontains=word)
            )

        queryset = User.objects.filter(user_type='agency', agency__isnull=False).filter(query)
        full_name_list = queryset.annotate(full_name=Concat('first_name', Value(' '), 'last_name')).values('full_name')
        full_name_list = [userobj['full_name'] for userobj in full_name_list]
        return full_name_list


    def get(self, request, user_type=None, search_str=None):
        if user_type not in ['influencer', 'brand', 'agency']:
            return JsonResponse({'error': 'Invalid user_type'})

        full_name_list = []
        if user_type == 'influencer':
            full_name_list = self.get_influencer_full_names(search_str)
        elif user_type == 'brand':
            full_name_list = self.get_brand_full_names(search_str)
        elif user_type == 'agency':
            full_name_list = self.get_agency_full_names(search_str)

        response_data = {'full_names': full_name_list}
        return JsonResponse(response_data)

class mobileUserProfileSearchView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, user_type=None):
        serializers_class = DashboardProfileSearchSerializer
        input_data = request.data
        profile = input_data['profile']

        queryset = User.objects.filter(user_type=user_type, verified_status='Verified')
        if user_type.lower() == 'brand':
            queryset = queryset.annotate(full_name=F('brand__company_name'))
        elif user_type.lower() == 'agency':
            queryset = queryset.annotate(full_name=F('agency__agency_name'))
        else:
            queryset = queryset.annotate(full_name=Concat('first_name', Value(' '), 'last_name'))

        if 'profile' in input_data.keys():
            profile = input_data['profile']
            if len(profile) > 0:
                queryset = queryset.filter(Q(full_name__icontains=profile))
        if 'gender' in input_data.keys():
            gender_list = input_data['gender']
            if len(gender_list) > 0:
                queryset = queryset.filter(gender__iregex=r'\y(' + '|'.join(gender_list) + r')\y')

        if 'age' in input_data.keys():
            age_range = input_data['age']
            if age_range:
                today = date.today()
                dob_range_start = today - timedelta(days=365 * age_range[1])
                dob_range_end = today - timedelta(days=365 * age_range[0])
                queryset = queryset.filter(Q(date_of_birth__range=[dob_range_start, dob_range_end]))

        if 'location' in input_data.keys():
            location_list = input_data['location']
            if len(location_list) > 0:
                queryset = queryset.filter(location__in=location_list)

        if 'content_category' in input_data.keys():
            content_category_list = input_data['content_category']
            if len(content_category_list) > 0:
                queryset = queryset.filter(content_category__content_category__in=content_category_list)
        serializer = serializers_class(queryset, many=True)
        serialized_data = serializer.data

        return Response(serialized_data)