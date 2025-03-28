import requests
from rest_framework import status
from collections import OrderedDict
from datetime import datetime
import random
import string

success_http_response = {'status': 'success',
                         'message': '{} created successfully',
                         'data': None}
success_http_code = status.HTTP_201_CREATED

failed_http_response = {
    'status': 'error',
    'message': '{} creation failed',
    'errors': None
}
failed_http_code = status.HTTP_400_BAD_REQUEST

success_http_response_template = {'response': success_http_response, 'code': success_http_code}
failed_http_response_template = {'response': failed_http_response, 'code': failed_http_code}


def validate_serializers_and_save(serializer_data):
    """
    This is utility function which will do the following tasks:
    1. Validate the serializer data
    2. Save the serializer data
    3. Generate the response dictionary and http code
    4. Return the response and code
    5. If its gets error, It will return Error response and http error code
    @param serializer_data:
    @return: response code and serializer data
    """
    model_name = serializer_data.Meta.model.__name__
    if serializer_data.is_valid():
        model_obj = serializer_data.save()
        model_obj.save()
        response = success_http_response_template['response']
        response['message'] = response['message'].format(model_name)
        response['data'] = serializer_data.data
        return response, success_http_response_template['code'], model_obj
    else:
        response = failed_http_response_template['response']
        response['message'] = response['message'].format(model_name)
        response['errors'] = serializer_data.errors
        return response, failed_http_response_template['code'], None


def validate_serializers(serializer_data):
    """
    Main purpose of this function is , Only validating the serializer data not saving!

    This is utility function which will do the following tasks:
    1. Validate the serializer data
    2. Generate the response dictionary and http code
    3. Return the response and code
    4. If its gets error, It will return Error response and http error code
    @param serializer_data:
    @return: response code and serializer data
    """
    model_name = serializer_data.Meta.model.__name__
    if serializer_data.is_valid():
        return {"status": "success"}, success_http_response_template['code']
    else:
        response = failed_http_response_template['response']
        response['message'] = response['message'].format(model_name)
        response['errors'] = serializer_data.errors
        return response, failed_http_response_template['code']


def create_fb_details_for_user(access_token, user_fb_model, user_id):
    # access_token = input_data.get('access_token', None)
    print(access_token)
    fields = 'id,name,email,picture,location,posts.limit(100),likes'
    url = f'https://graph.facebook.com/me?fields={fields}&access_token={access_token}'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        facebook_id = data.get('id', '')
        name = data.get('name', '')
        email = data.get('email', '')
        try:
            picture = data.get('picture', '')
            picture = picture['data']['url']
        except:
            picture = None

        try:
            total_posts = len(data['posts']['data'])
        except:
            total_posts = None
        data = {'user_id': None, 'no_of_posts': total_posts, 'fb_id': facebook_id,
                'fb_name': name, 'fb_email': email, 'fb_profile_pic_link': picture}
        # replace 'MyModel' with the name of your model
        social_data = user_fb_model.objects.create(**data)
        return social_data


def convert_ordered_dict_to_dict(data):
    if isinstance(data, OrderedDict):
        return dict((key, convert_ordered_dict_to_dict(value)) for key, value in data.items())
    elif isinstance(data, list):
        return [convert_ordered_dict_to_dict(item) for item in data]
    else:
        return data


def convert_datetime_format(date_data, date_format):
    try:
        return datetime.strftime(date_data, date_format)
    except:
        return ''


def generate_file_name(suffix_str=''):
    current_datetime = datetime.now()
    random_number = ''.join(random.choices(string.digits, k=6))
    file_name = current_datetime.strftime("%Y-%m-%d_%H-%M-%S") + "_" + random_number + suffix_str
    return file_name

def concat_names(user_obj):
    f_name = user_obj.first_name if user_obj.first_name is not None else ''
    l_name = user_obj.last_name if user_obj.last_name is not None else ''
    return str(f_name) + ' ' + str(l_name)
def get_user_name(obj):
    user_type = obj.user_type
    if user_type == 'brand':
        brand = obj.brand
        if brand and brand.company_name:
            return brand.company_name
        else:
            return concat_names(obj)
    elif user_type == 'agency':
        agency = obj.agency
        if agency and agency.agency_name:
            return agency.agency_name
        else:
            return concat_names(obj)
    else:
        return concat_names(obj)
