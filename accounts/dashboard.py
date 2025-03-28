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
from .serializers import UserSerializer, InfluencerSerializer, AgencySerializer, BrandSerializer, \
    UserFullNameMetaSerializer, DashboardProfileSearchSerializer
from .models import User, Brand, Influencer, Agency, LocationCityMaster
from .utils import get_user_type_serializer, user_search_fields_dict, get_user_type_serializer_explicitly, \
    get_user_custom_details_by_id, common_search_feilds
from django.db.models import F
from django.db.models import Value
from django.db.models.functions import Concat


class UserSearchView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    queryset = User.objects.all()

    def get_serializer_class(self):
        user_type = self.kwargs['user_type']
        return get_user_type_serializer_explicitly(user_type)

    def get_search_fields(self):
        user_type = self.kwargs['user_type']
        return user_search_fields_dict.get(user_type, None)

    def get_queryset(self):
        user_type = self.kwargs['user_type']
        queryset = User.objects.all()
        search_query = self.request.query_params.get('q', None)
        search_feilds = self.get_search_fields()
        queryset = queryset.filter(user_type=user_type, verified_status='Verified')
        if search_feilds:
            q_list = [Q(**{f'{field}__icontains': search_query}) for field in search_feilds]
            query = Q()
            for q in q_list:
                query |= q
            if search_query is not None:
                queryset = queryset.filter(query)
        return queryset

import operator
class UserSearchMetaView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_type=None):
        queryset = User.objects.annotate(value=F('id'), label=Concat('first_name',
                                                                     Value(' '), 'last_name'), type=Value('profile'))
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
        # generate content category Meta:
        content_queryset = ContentCategory.objects.annotate(value=F('id'), label=F('content_category'),
                                                            type=Value('content_category'))
        content_queryset = content_queryset.filter(
            Q(content_category__icontains=search_query)
        )
        content_dict = list(content_queryset.values('value', 'label', 'type'))
        merged_list = user_dict + content_dict
        return JsonResponse({"data": merged_list}, safe=False)


class UserBrandDetailsByIdView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id=None):
        return get_user_custom_details_by_id(user_id, Brand, BrandSerializer, user_type='brand')


class UserAgencyDetailsByIdView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id=None):
        return get_user_custom_details_by_id(user_id, Agency, AgencySerializer, user_type='agency')


class UserInfluencerDetailsByIdView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id=None):
        return get_user_custom_details_by_id(user_id, Influencer, InfluencerSerializer, user_type='influencer')


class UserProfileSearchMetaView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserFullNameMetaSerializer

    def get_influencer_full_names(self, search_str):
        queryset = User.objects.filter(user_type='influencer', verified_status='Verified')
        queryset = queryset.annotate(full_name=Concat('first_name', Value(' '), 'last_name'))
        queryset = queryset.filter(Q(full_name__icontains=search_str)).values('full_name')
        full_name_list = [userobj['full_name'] for userobj in queryset]
        return full_name_list

    def get_brand_full_names(self, search_str):
        queryset = User.objects.filter(user_type='brand', verified_status='Verified')
        queryset = queryset.annotate(brand_name=F('brand__company_name'))
        queryset = queryset.filter(Q(brand_name__icontains=search_str)).values('brand_name')
        full_name_list = [userobj['brand_name'] for userobj in queryset]
        return full_name_list

    def get_agency_full_names(self, search_str):
        queryset = User.objects.filter(user_type='agency', verified_status='Verified')
        queryset = queryset.annotate(agency_name=F('agency__agency_name'))
        queryset = queryset.filter(Q(agency_name__icontains=search_str)).values('agency_name')
        full_name_list = [userobj['agency_name'] for userobj in queryset]
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
        full_name_list = full_name_list[:5]
        response_data = {'full_names': full_name_list}
        return JsonResponse(response_data)


class UserProfileSearchView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, user_type=None):
        serializers_class = DashboardProfileSearchSerializer
        input_data = request.data

        queryset = User.objects.filter(user_type=user_type, verified_status='Verified')
        if user_type.lower() == 'brand':
            queryset = queryset.annotate(full_name=F('brand__company_name'))
        elif user_type.lower() == 'agency':
            queryset = queryset.annotate(full_name=F('agency__agency_name'))
        else:
            queryset = queryset.annotate(full_name=Concat('first_name', Value(' '), 'last_name'))

        if 'profile' in input_data.keys():
            profile = input_data['profile']
            if len(profile)>0:
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


class LocationCitySearchMetaView(APIView):
    def get(self, request):
        search_query = self.request.query_params.get('q', None)
        queryset = LocationCityMaster.objects.annotate(value=F('city_name'), label=F('city_name'))
        queryset = queryset.filter(
            Q(city_name__icontains=search_query)
        )
        city_dict = list(queryset.values('value', 'label'))[:10]
        return JsonResponse({"data": city_dict}, safe=False)