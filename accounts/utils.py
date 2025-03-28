from django.http import JsonResponse

from accounts.models import Influencer, BrandMedia, Agency, Brand, AgencyMedia, User, EmailOTP
from accounts.serializers import UserInfluencerSerializer, UserAgencySerializer, UserBrandSerializer, \
    UserSerializer, BrandSerializer, AgencySerializer, InfluencerSerializer
from helpers.utils import convert_ordered_dict_to_dict

user_models_dict = {"influencer": Influencer, "agency": Agency, "brand": Brand}
user_file_models_dict = {"agency": AgencyMedia, "brand": BrandMedia}

user_search_fields = ['first_name', 'last_name', 'username', 'content_category__content_category', ]
agency_search_fields = ['agency__agency_name']
brand_search_fields = ['brand__brand_name']

user_search_fields_dict = {"influencer": user_search_fields, "agency": user_search_fields + agency_search_fields,
                           "brand": user_search_fields + brand_search_fields}

user_type_alone_serializer = {"influencer": InfluencerSerializer, "agency": AgencySerializer, "brand": BrandSerializer}

common_search_feilds = {"Location":'location','Gender':'gender','Age':'age_in_years'}
def get_user_type_serializer(user):
    print(user.user_type)
    if user.user_type == 'influencer':
        return UserInfluencerSerializer
    elif user.user_type == 'agency':
        return UserAgencySerializer
    elif user.user_type == 'brand':
        return UserBrandSerializer
    else:
        return UserSerializer


def get_user_type_serializer_explicitly(user_type):
    if user_type == 'influencer':
        return UserInfluencerSerializer
    elif user_type == 'agency':
        return UserAgencySerializer
    elif user_type == 'brand':
        return UserBrandSerializer
    else:
        return UserSerializer


def get_user_custom_details_by_id(user_id, user_type_model, user_type_serialiser, user_type):
    try:
        queryset = User.objects.filter(id=user_id)
        serialized_data = UserSerializer(queryset, many=True).data
        data_list = []
        for item in serialized_data:
            data_dict = convert_ordered_dict_to_dict(item)
            data_list.append(data_dict)

        if data_list:
            user_data = data_list[0]
            if user_data['user_type'] == user_type:
                queryset = user_type_model.objects.filter(user_id=user_id)
                serialized_data = user_type_serialiser(queryset, many=True).data
                brand_data_list = []
                for item in serialized_data:
                    data_dict = convert_ordered_dict_to_dict(item)
                    brand_data_list.append(data_dict)
                if brand_data_list:
                    brand_data = brand_data_list[0]
                    try:
                        del brand_data['id']
                    except:
                        pass
                    user_data.update(brand_data)
            else:
                return JsonResponse(
                    {"data": [], "msg": "Requested {} data doesnt exists ".format(str(user_type_model.__name__))},
                    safe=False)
        return JsonResponse({"data": user_data}, safe=False)
    except Exception as e:
        return JsonResponse({"data": [], "msg": "Failed to get the {} details".format(str(user_type_model.__name__))},
                            safe=False)


def check_email_exists(email):
    try:
        user_obj = User.objects.get(email=email)
    except User.DoesNotExist:
        user_obj = None
    return user_obj


