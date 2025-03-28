import json

from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.conf import settings
from django.contrib.auth import login
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from rest_auth import serializers
from rest_framework import generics, permissions, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.parsers import FileUploadParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import UpdateAPIView
from rest_framework.permissions import IsAuthenticated
import requests
from helpers.utils import validate_serializers_and_save, validate_serializers, create_fb_details_for_user, get_user_name,concat_names
from .cometchatapi import create_cometchat_profile, update_cometchat_profile
from .models import User, SocialMediaData, Influencer, BookmarkedUsers, ContentCategory, Campaign, Brand, HotiMedia, \
    CampaignMedia, Agency, UserWishList, AgencyMedia, BrandMedia, UserFbDetails, UserWishListItems, UserInstaDetails
from .serializers import UserSerializer, UserListSerializer, UserInfluencerSerializer, UserBrandSerializer, \
    UserAgencySerializer, UserProfileImageSerializer, DashboardSerializer, InfluencerSerializer, CampaignSerializer, \
    HotiMediaSerializer, UserMetaSerializer, UserWishListSerializer, UserWishListItemsSerializer, \
    ManyUploadFileSerializer, AgencySerializer, UserWishListByShareIdSerializer
from django.db.models import Case, When, Exists, OuterRef
from django.core.files.storage import default_storage
from rest_framework.parsers import MultiPartParser
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from .utils import get_user_type_serializer, user_models_dict, user_file_models_dict, user_type_alone_serializer
from .serializers import ChangePasswordSerializer

from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
User = get_user_model()


expiry_sec = settings.TOKEN_EXPIRY_IN_SEC


class CustomObtainAuthToken(ObtainAuthToken):

    def post(self, request, *args, **kwargs):
        """

        @param request: user auth login request data (username and password)
        @param args:
        @param kwargs:
        @return: auth token along with user details
        """
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)

        # Set token expiration time (in seconds)
        token_expire_seconds = int(expiry_sec)  # 1 day
        token.expires = timezone.now() + timezone.timedelta(seconds=token_expire_seconds)
        token.save()
        refresh_token = token.generate_key()
        user.refresh_token = refresh_token
        user.save()

        return Response({
            'user_id': user.id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'dob': user.date_of_birth,
            'email': user.email,
            'age': user.age_in_years,
            'facebook': user.facebook,
            'instagram': user.instagram,
            'user_type': user.user_type,
            'token': token.key,
            'expiry_time': token.expires,
            'refresh_token': refresh_token,
            'profile_image': user.user_profile_image_if_exists,
            'verified_status': user.verified_status
        })


class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Delete the authentication token
        Token.objects.filter(user=request.user).delete()
        return Response({'detail': 'Successfully logged out.'})


class UserListCreateView(generics.ListCreateAPIView):
    """
    Return all users
    """
    queryset = User.objects.all()
    serializer_class = UserListSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)


class CreateUserAPIView(APIView):
    def post(self, request):
        """

        @param request: user base details like username,password, firstname,lastname, user type, etc.
        @return: user details

        @note: we're having three user type fields in user model(is_influencer, is_agency, is_brand boolean fields)
        based on user type is true, calling the respective serializer to create the user
        """
        base_serializer = UserSerializer(data=request.data)
        if request.data.get('user_type', None) == 'influencer':
            serializer = UserInfluencerSerializer(data=request.data)
        if request.data.get('user_type', None) == 'brand':
            serializer = UserBrandSerializer(data=request.data)
        if request.data.get('user_type', None) == 'agency':
            serializer = UserAgencySerializer(data=request.data)
        response, code = validate_serializers(base_serializer)
        if code == 400:
            return Response(response, status=code)
        response, code, model_obj = validate_serializers_and_save(serializer)
        """ Set encode password for the user after the user creation , by default it wont set the encoded password"""
        if model_obj:
            model_obj.set_password(request.data.get('password'))
            model_obj.save()
            try:
                user_data = response['data']
                profile_image_url = user_data.get('profile_image')
                username = user_data.get('username')
                user_id = user_data.get('id')
                user_type = user_data.get('user_type')
                cometchat = create_cometchat_profile(user_id, profile_image_url, username, get_user_name(model_obj),
                                                     user_type)
            except:
                pass


        try:
            access_token = request.data.get('fb_access_token')['accessToken']
            social_data = create_fb_details_for_user(access_token, UserFbDetails, model_obj.id)
        except:
            pass

        return Response(response, status=code)
    



class UserProfileImageView(UpdateAPIView):
    parser_classes = (MultiPartParser,)
    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileImageSerializer

    def get_object(self):
        return self.request.user



    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        try:
            user_obj = self.get_object()
            profile_image_url = user_obj.profile_image.url
            username = user_obj.username
            user_id = user_obj.id
            user_type = user_obj.user_type
            # Update the profile image in CometChat
            cometchat = update_cometchat_profile(user_id,profile_image_url, username, get_user_name(user_obj), user_type)
        except:
            pass

        return Response({'detail': 'Profile image updated successfully.'}, status=status.HTTP_200_OK)
   
class UploadFileView(generics.CreateAPIView):
    """
     @return: s3 profile_image_url and user_id for requested user by using auth token

     """
    parser_classes = (MultiPartParser,)

    serializer_class = HotiMediaSerializer

    def post(self, request, format=None):
        serializer = ManyUploadFileSerializer(data=request.data)
        if serializer.is_valid():  # validate the serialized data to make sure its valid
            qs = serializer.save()
            message = {'detail': qs, 'status': True}
            return Response(message, status=status.HTTP_201_CREATED)
        else:  # if the serialzed data is not valid, return erro response
            data = {"detail": serializer.errors, 'status': False}
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
    #
    # def get_queryset(self):
    #     return HotiMedia.objects.all()


class FBClass(APIView):
    def post(self, request):
        input_data = request.data
        access_token = input_data.get('access_token', None)
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
            social_data = UserFbDetails.objects.create(**data)
            socialdataid = social_data.id
            msg = "success"
            error = ''
            status_code = status.HTTP_201_CREATED
        else:
            print(f'Error retrieving user data: {response.content}')
            socialdataid = None
            msg = "failed"
            error = f'Error retrieving user data: {response.content}'
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return Response({"social_data_id": socialdataid, "msg": msg, "error": error}, status=status_code)


def get_influencer_data_for_dashboard(request):
    user_id = request.user.id
    content_categories = ContentCategory.objects.filter(user_content__id=user_id)
    related_users = User.objects.filter(content_category__in=content_categories, user_type='influencer',
                                        verified_status='Verified').exclude(
        id=user_id).distinct().all()
    serialized_recom = DashboardSerializer(related_users, many=True, context={'request': request}).data

    data_a = User.objects.filter(user_type='influencer', verified_status='Verified').all()
    serialized_inf = DashboardSerializer(data_a, many=True, context={'request': request}).data
    inf_trend_data = {"title": "Popular Influencers on HOTI",
                      'data': serialized_inf
                      }
    inf_recommend_data = {"title": "Recommended Influencers For You",
                          'data': serialized_recom
                          }
    return inf_trend_data, inf_recommend_data


def get_brand_data_for_dashboard(request):
    user_id = request.user.id
    if request.user.user_type == 'influencer':
        content_categories = Influencer.objects.values('interests__id').filter(user_id=user_id)
    else:
        content_categories = ContentCategory.objects.filter(user_content__id=user_id)
    related_users = User.objects.filter(content_category__in=content_categories, user_type='brand',
                                        verified_status='Verified').exclude(
        id=user_id).distinct().all()
    serialized_recom = DashboardSerializer(related_users, many=True, context={'request': request}).data

    data_a = User.objects.filter(user_type='brand', verified_status='Verified').all()
    serialized_inf = DashboardSerializer(data_a, many=True, context={'request': request}).data
    brand_trend_data = {"title": "Popular Brands on HOTI",
                        'data': serialized_inf
                        }
    brand_recommend_data = {"title": "Recommended Brands For You",
                            'data': serialized_recom
                            }
    return brand_trend_data, brand_recommend_data


def get_agency_data_for_dashboard(request):
    user_id = request.user.id
    if request.user.user_type == 'influencer':
        content_categories = Influencer.objects.values('interests__id').filter(user_id=user_id)
    else:
        content_categories = ContentCategory.objects.filter(user_content__id=user_id)
    related_users = User.objects.filter(content_category__in=content_categories, user_type='agency',
                                        verified_status='Verified').exclude(id=user_id).distinct().all()

    data_a = User.objects.filter(user_type='agency', verified_status='Verified').all()
    serialized_inf = DashboardSerializer(data_a, many=True, context={'request': request}).data
    serialized_recom = DashboardSerializer(related_users, many=True, context={'request': request}).data
    brand_trend_data = {"title": "Popular Agency on HOTI",
                        'data': serialized_inf
                        }
    brand_recommend_data = {"title": "Recommended Agency For You",
                            'data': serialized_recom
                            }
    return brand_trend_data, brand_recommend_data


class AllTypeOfUserListView(APIView):
    """
    Return all users
    """

    def get(self, request):
        # create the data objects
        data = []
        if request.user.user_type == 'agency':
            inf_trend_data, inf_recommend_data = get_influencer_data_for_dashboard(request)
            brand_trend_data, brand_recommend_data = get_brand_data_for_dashboard(request)
            data = [inf_trend_data, inf_recommend_data, brand_trend_data, brand_recommend_data]
        if request.user.user_type == 'brand':
            inf_trend_data, inf_recommend_data = get_influencer_data_for_dashboard(request)
            agency_trend_data, agency_recommend_data = get_agency_data_for_dashboard(request)
            data = [inf_trend_data, inf_recommend_data, agency_trend_data, agency_recommend_data]

        if request.user.user_type == 'influencer':
            brand_trend_data, brand_recommend_data = get_brand_data_for_dashboard(request)
            agency_trend_data, agency_recommend_data = get_agency_data_for_dashboard(request)
            data = [brand_trend_data, brand_recommend_data, agency_trend_data, agency_recommend_data]

        serialized_data = {"data": data}

        # return the serialized data in a JSON response
        return Response(serialized_data)


class InfluencerUserDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserInfluencerSerializer

    def get_object(self):
        user_id = self.kwargs.get('user_id')
        return User.objects.get(pk=user_id)


class UserDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        user = self.request.user
        return get_user_type_serializer(user)

    def get_object(self):
        user = self.request.user
        user_id = user.id
        return User.objects.get(pk=user_id)


class UserDetailByIdAPIView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        user = self.get_object()
        serializer_class = get_user_type_serializer(user)
        return serializer_class

    def get_object(self):
        user_id = self.kwargs.get('user_id')
        return User.objects.get(pk=user_id)


class InfluencerUpdateAPIView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserInfluencerSerializer
    lookup_field = 'user_id'

    def get_queryset(self):
        influencer_id = self.kwargs['user_id']
        return Influencer.objects.filter(id=influencer_id)

    def update(self, request, *args, **kwargs):
        influencer_id = self.kwargs['user_id']
        input_data = request.data
        influencer_data = input_data.pop('influencer', {})
        influencer = Influencer.objects.get(user_id=influencer_id)
        influencer_serializer = InfluencerSerializer(influencer, data=influencer_data, partial=True)
        if influencer_serializer.is_valid():
            influencer_serializer.save()
        else:
            print(influencer_serializer.errors)
            raise serializers.ValidationError(influencer_serializer.errors)

        user_obj = User.objects.get(id=influencer.user.id)
        content_data = input_data.pop('content_category', {})
        serializer = UserSerializer(user_obj, data=input_data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        content_category_list = []
        for con_data in content_data:
            content, created = ContentCategory.objects.get_or_create(content_category=con_data['content_category'])
            user_obj.content_category.add(content)
            content_category_list.append(content)
        user_obj.content_category_list = content_category_list
        user_obj.influencer = influencer
        return Response(UserInfluencerSerializer(user_obj).data)


def update_user_content(user_id, input_data, user_type, serializer_class, user_model, user_file_model):
    user_type_data = input_data.pop(user_type, None)
    content_data = input_data.pop('content_category') if 'content_category' in input_data else []
    user_type_data = user_type_data if user_type_data else {}
    interests_data = user_type_data.pop('interests', None) if 'interests' in user_type_data else []

    files_data = user_type_data.pop('file_ids', None) if 'file_ids' in user_type_data else []
    user_model_instance = user_model.objects.get(user_id=user_id)
    if user_type_data:
        user_type_serializer_class = user_type_alone_serializer.get(user_type, UserSerializer)

        serializer_data = user_type_serializer_class(user_model_instance, data=user_type_data, partial=True)
        if serializer_data.is_valid():
            user_model_updated_instance = serializer_data.save()
        else:
            raise serializers.ValidationError(serializer_class.errors)

    user_obj = User.objects.get(id=user_id)
    # content_data = input_data.pop('content_category', {})
    serializer = UserSerializer(user_obj, data=input_data, partial=True)
    serializer.is_valid(raise_exception=True)
    serializer.save()

    content_category_list = []
    content_category_list_ids = []
    if content_data:
        for con_data in content_data:
            try:
                content = ContentCategory.objects.get(content_category=con_data['content_category'])
                # user_obj.content_category.add(content)
                content_category_list_ids.append(content.id)
            except Exception as e:
                pass
        user_obj.content_category.clear()
        user_obj.content_category.add(*content_category_list_ids)
        user_obj.content_category_list = content_category_list

    # user_obj.influencer = user_model_instance

    if user_type == 'influencer':
        if interests_data:
            interest_list = []
            interest_list_ids = []
            for int_data in interests_data:
                try:
                    interest_ = ContentCategory.objects.get(content_category=int_data['interest_name'])
                    interest_list_ids.append(interest_.id)
                except Exception as e:
                    pass
            user_model_instance.interests.clear()
            user_model_instance.interests.add(*interest_list_ids)

            # user_model_updated_instance.interest_list = interest_list

    if user_type_data:
        if user_type in ['agency', 'brand']:
            user_files_related_str = 'agency_media' if user_type == 'agency' else 'brand_media'
            user_files_related_str_set = 'agency_files' if user_type == 'agency' else 'brand_files'
            user_file_media_list = []
            user_file_media_list_ids = []
            if files_data:
                if user_type == 'agency':
                    ids_to_remove = user_model_instance.agency_files.all().values_list('id', flat=True)
                    AgencyMedia.objects.filter(id__in=ids_to_remove).delete()
                if user_type == 'brand':
                    ids_to_remove = user_model_instance.brand_files.all().values_list('id', flat=True)
                    BrandMedia.objects.filter(id__in=ids_to_remove).delete()

                for media_data in files_data:
                    media = HotiMedia.objects.get(id=media_data)
                    media_file_dict = {user_type: user_model_instance, 'media_file': media}
                    user_file_media = user_file_model.objects.create(**media_file_dict)
                    user_file_media.save()
                    user_file_media_list.append(user_file_media)
                    user_file_media_list_ids.append(user_file_media.id)

                # user_model_updated_instance.interests.add(*interest_list_ids)

                setattr(user_model_instance, user_files_related_str, user_file_media_list)

        setattr(user_obj, user_type, user_model_instance)

    return serializer_class(user_obj).data


from .utils import get_user_custom_details_by_id


class UserUpdateAPIView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]

    # serializer_class = UserInfluencerSerializer
    # lookup_field = 'user_id'

    def get_serializer_class(self):
        user = self.request.user
        return get_user_type_serializer(user)

    def get_queryset(self):
        # influencer_id = self.kwargs['user_id']
        user_id = self.request.user.id
        user_type = self.request.user.user_type
        user_model = user_models_dict.get(user_type, None)
        return User.objects.filter(id=user_id)

    def update(self, request, *args, **kwargs):
        user_id = self.request.user.id
        user_type = self.request.user.user_type
        if 'application/json' in request.content_type:
            # JSON data
            input_data = request.data
        elif 'multipart/form-data' in request.content_type:
            # FormData
            input_data = request.POST.dict()
            # input_data = json.dumps(form_data)

        # input_data = request.data

        user_model = user_models_dict.get(user_type, None)
        serializer_class = get_user_type_serializer(self.request.user)

        user_file_model = user_file_models_dict.get(user_type, user_type)

        if user_model:
            user_updated_data = update_user_content(user_id, input_data, user_type, serializer_class, user_model,
                                                    user_file_model)
            serializer_indvidual_class = user_type_alone_serializer.get(user_type, None)
            return get_user_custom_details_by_id(user_id, user_model, serializer_indvidual_class, user_type)

            # return Response(user_updated_data)
        else:
            return Response({"message": "Unidentified user type"}, status=status.HTTP_404_NOT_FOUND)


class CampaignCreateAPIView(APIView):
    def post(self, request):
        input_data = request.data
        base_serializer = CampaignSerializer(data=input_data)
        if base_serializer.is_valid():
            associated_brands_id = input_data.pop('associated_brands', None)
            associated_influencers_data = input_data.pop('associated_influencers', [])
            content_data = input_data.pop('content_category', [])
            campaign_files = input_data.pop('campaign_files', [])

            input_data['user_id'] = request.user.id

            try:
                brand = Brand.objects.get(user_id=associated_brands_id)
                input_data['associated_brands_id'] = brand.id
            except ObjectDoesNotExist:
                return Response({"Error":"Associated brand doesnt exists"}, status=status.HTTP_404_NOT_FOUND)

            campaign = Campaign.objects.create(**input_data)

            associated_brands_list = []
            associated_influencers_list = []
            content_category_list = []
            campaign_media_list = []

            for influencers_data in associated_influencers_data:
                try:
                    influencers = Influencer.objects.get(user_id=influencers_data)
                    campaign.associated_influencers.add(influencers)
                    associated_influencers_list.append(influencers)
                except ObjectDoesNotExist:
                    pass

            for con_data in content_data:
                content, created = ContentCategory.objects.get_or_create(content_category=con_data['content_category'])
                campaign.content_category.add(content)
                content_category_list.append(content)

            for media_data in campaign_files:
                try:
                    media = HotiMedia.objects.get(id=media_data)
                    campaign_media = CampaignMedia.objects.create(campaign=campaign, media_file=media)
                    campaign_media.save()
                    campaign_media_list.append(campaign_media)
                except ObjectDoesNotExist:
                    pass

            campaign.save()
            campaign.campaign_media = campaign_media_list
        else:
            return Response(base_serializer.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(CampaignSerializer(campaign).data, status=status.HTTP_201_CREATED)


class CampaignListAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CampaignSerializer

    def get_queryset(self):
        user_id = self.request.user.id
        return Campaign.objects.filter(user_id=user_id)


class UserTypeListAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserMetaSerializer

    def get_queryset(self):
        user_type = self.kwargs['user_type']
        return User.objects.filter(user_type=user_type)


class UserWishListCreateView(generics.CreateAPIView):
    queryset = UserWishList.objects.all()
    serializer_class = UserWishListSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            try:
                serializer.save(user=request.user)  # Assign the current user to the user field
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except IntegrityError:
                raise serializers.ValidationError({'detail': 'A wishlist with this name already exists for this user.'},
                                                  status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserWishListView(generics.ListAPIView):
    serializer_class = UserWishListSerializer

    def get_queryset(self):
        return UserWishList.objects.filter(user=self.request.user)


class UserWishListItemsDeleteView(generics.DestroyAPIView):
    queryset = UserWishListItems.objects.all()
    serializer_class = UserWishListItemsSerializer

    def post(self, request, *args, **kwargs):
        user_id = self.request.data.get('user_id')
        user_wish_list_id = self.request.data.get('user_wish_list_id')

        try:
            user_wish_list = UserWishList.objects.get(id=user_wish_list_id, user=request.user)
        except UserWishList.DoesNotExist:
            return Response({'detail': 'Wishlist not found'}, status=status.HTTP_404_NOT_FOUND)

        wishlist_item = get_object_or_404(self.queryset, user=user_id, user_wish_list=user_wish_list)
        wishlist_item.delete()

        wishlists = UserWishList.objects.filter(user=request.user)
        serializer = UserWishListSerializer(wishlists, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserWishListItemsAPIView(generics.CreateAPIView):
    queryset = UserWishListItems.objects.all()
    serializer_class = UserWishListItemsSerializer

    def post(self, request, *args, **kwargs):
        user_id = request.data.get('user')
        user_wish_list_id = request.data.get('user_wish_list')
        try:
            user_wish_list = UserWishList.objects.get(id=user_wish_list_id, user=request.user)
        except UserWishList.DoesNotExist:
            return Response({'detail': 'Wishlist not found'}, status=status.HTTP_404_NOT_FOUND)

            # Retrieve the user from the User model
        user = User.objects.get(id=user_id)

        # Get the profile_image of the user
        is_user_exists_in_wishlist_already = UserWishListItems.objects.filter(user_id=user.id,user_wish_list_id=user_wish_list.id).first()
        if is_user_exists_in_wishlist_already:
            return Response({'detail': 'User already mapped with this wishlist'}, status=status.HTTP_208_ALREADY_REPORTED)
        input_data = {
            'user': user.id,
            'user_wish_list':user_wish_list.id,
            # 'profile_image': profile_image,  # Add the profile_image to the input data
        }
        serializer = self.get_serializer(data=input_data)
        if serializer.is_valid():
            serializer.save()
            wishlists = UserWishList.objects.filter(user=request.user)
            serializer = UserWishListSerializer(wishlists, many=True, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserWishListDeleteView(APIView):
    queryset = UserWishList.objects.all()
    serializer_class = UserWishListSerializer

    def post(self, request, *args, **kwargs):
        wishlist_id = request.data.get('wishlist_id')
        print(f'wishlist_id: {wishlist_id}')
        try:
            wishlist = self.queryset.get(pk=wishlist_id, user=request.user)
            print(f'wishlist: {wishlist}')
            wishlist.delete()
        except UserWishList.DoesNotExist:
            return Response({'detail': 'Wishlist not found'}, status=status.HTTP_404_NOT_FOUND)

        wishlists = UserWishList.objects.filter(user=request.user)
        serializer = UserWishListSerializer(wishlists, many=True, context={'request': request})

        return Response(serializer.data, status=status.HTTP_200_OK)

class CampaignDeleteView(APIView):
    queryset = Campaign.objects.all()
    serializer_class = CampaignSerializer
    def post(self, request, *args, **kwargs):
        campaign_id = request.data.get('campaign_id')
        try:
            campaign = self.queryset.get(pk=campaign_id, user=request.user)
            campaign.delete()
        except Campaign.DoesNotExist:
            return Response({'detail': 'Campaign not found'}, status=status.HTTP_404_NOT_FOUND)

        campaigns = Campaign.objects.filter(user=request.user)
        serializer = CampaignSerializer(campaigns, many=True, context={'request': request})

        return Response(serializer.data, status=status.HTTP_200_OK)

class UserWishListRenameView(APIView):
    queryset = UserWishList.objects.all()
    serializer_class = UserWishListSerializer

    def post(self, request, *args, **kwargs):
        wishlist_id = request.data.get('wishlist_id')
        new_name = request.data.get('new_name')

        try:
            wishlist = self.queryset.get(pk=wishlist_id, user=request.user)
            wishlist.list_name = new_name
            wishlist.save()
        except UserWishList.DoesNotExist:
            return Response({'detail': 'Wishlist not found'}, status=status.HTTP_404_NOT_FOUND)

        wishlists = UserWishList.objects.filter(user=request.user)
        serializer = UserWishListSerializer(wishlists, many=True, context={'request': request})

        return Response(serializer.data, status=status.HTTP_200_OK)


class InstaClass(APIView):
    def post(self, request):
        input_data = request.data
        access_token = input_data.get('access_token', None)
        print(access_token)
        fields = 'followers_count,follows_count,id,media_count,username,name'
        url = f'https://graph.instagram.com/me?fields={fields}&access_token={access_token}'
        response = requests.get(url)
        print(response.status_code)
        if response.status_code == 200:
            data = response.json()
            response_data = {
                "followers_count": data.get('followers_count', 0),
                "follows_count": data.get('follows_count', 0),
                "id": data.get('id', ''),
                "media_count": data.get('media_count', 0),
                "username": data.get('username', ''),
                "name": data.get('name', '')
            }
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            print(f'Error retrieving user data: {response.content}')
            return Response({"error": "failed to retrive data"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




class ChangePasswordView(generics.UpdateAPIView):
    """
    An endpoint for changing password.
    """
    serializer_class = ChangePasswordSerializer
    model = User
    permission_classes = (IsAuthenticated,)

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj

    def update(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            # Check old password
            if not self.object.check_password(serializer.data.get("old_password")):
                return Response({"old_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)
            # set_password also hashes the password that the user will get
            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()
            response = {
                'status': 'success',
                'code': status.HTTP_200_OK,
                'message': 'Password updated successfully',
                'data': []
            }

            return Response(response)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserWishListByShareListIdView(generics.ListAPIView):
    queryset = UserWishList.objects.all()
    serializer_class = UserWishListByShareIdSerializer


    def get_queryset(self):
        share_list_id = self.kwargs['share_list_id']
        return self.queryset.filter(id=share_list_id)

