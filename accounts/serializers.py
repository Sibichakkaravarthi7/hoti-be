from django.db.models import F, CharField
from django.forms import model_to_dict
from rest_framework import serializers
from django.db.models import Value
from django.db.models.functions import Concat
from helpers.utils import convert_datetime_format,get_user_name,concat_names
from hoti.settings import AWS_S3_CUSTOM_DOMAIN
from .models import User, Influencer, Brand, Agency, BookmarkedUsers, Campaign, HotiMedia, CampaignMedia, UserWishList, \
    UserWishListItems, AgencyMedia, BrandMedia, UserFbDetails
from master.models import ContentCategory
from master.serializers import ContentCategorySerializer, InterestSerializer
from datetime import datetime
from django.conf import settings



def create_user_content(validated_data, user_type, user_type_model,user_file_model=None):
    user_type_data = validated_data.pop(user_type, None)
    content_data = validated_data.pop('content_category')

    interests_data = user_type_data.pop('interests', None)
    files_data = user_type_data.pop('file_ids', None)

    user = User.objects.create(**validated_data)
    user_obj = user_type_model.objects.create(user=user, **user_type_data)
    content_category_list = []
    for con_data in content_data:
        try:
            content_category = con_data['content_category']
            content = ContentCategory.objects.get(content_category=content_category)
            user.content_category.add(content)
            content_category_list.append(content)
        except Exception as e:
            pass
    user.content_category_list = content_category_list

    if user_type == 'influencer':
        if interests_data:
            interest_list = []
            for int_data in interests_data:
                try:
                    interest_ = ContentCategory.objects.get(content_category=int_data['content_category'])
                    user_obj.interests.add(interest_)
                    interest_list.append(interest_)
                except Exception as e:
                    pass
            user.interest_list = interest_list

    if user_type in ['agency', 'brand']:
        user_files_related_str = 'agency_media' if user_type == 'agency' else 'brand_media'
        user_file_media_list = []
        if files_data:
            for media_data in files_data:
                media = HotiMedia.objects.get(id=media_data)
                media_file_dict = {user_type: user_obj, 'media_file': media}
                user_file_media = user_file_model.objects.create(**media_file_dict)
                user_file_media.save()
                user_file_media_list.append(user_file_media)
            setattr(user_obj, user_files_related_str, user_file_media_list)
    return user, user_obj


class HotiMediaSerializer(serializers.ModelSerializer):
    """
    @note: This serializer for handling profile image of user
    """

    class Meta:
        model = HotiMedia
        fields = '__all__'



class UserFBDetailsSerializer(serializers.ModelSerializer):
    """
    @note: This serializer for handling fb data of user
    """

    class Meta:
        model = UserFbDetails
        fields = '__all__'

class AgencyMediaSerializer(serializers.ModelSerializer):
    media_file = HotiMediaSerializer()

    class Meta:
        model = AgencyMedia
        fields = ('id', 'agency', 'media_file')


class BrandMediaSerializer(serializers.ModelSerializer):
    media_file = HotiMediaSerializer()
    class Meta:
        model = BrandMedia
        fields = ('id', 'brand', 'media_file')



class InfluencerSerializer(serializers.ModelSerializer):
    interests = InterestSerializer(many=True)
    featured_posts = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Influencer
        fields = ('interests_in_our_news_letter','fb_access_token','interests','featured_posts')

    def get_featured_posts(self, obj):
        try:
            MEDIA_URL = settings.MEDIA_URL

            campaign_list = CampaignMedia.objects.filter(campaign__user__id=obj.user_id).annotate(
                media_file__media_file=Concat(Value(MEDIA_URL),'media_file__media_file', output_field=CharField() ))
            campaign_list = list(campaign_list.values('media_file__media_file',
                                                      'media_file__file_type'))

            return campaign_list
        except Exception as e:
            raise e
            return []


class BrandSerializer(serializers.ModelSerializer):
    brand_files = BrandMediaSerializer(many=True,read_only=True)
    file_ids = serializers.ListField(child=serializers.IntegerField(), required=False)
    profile_image = serializers.SerializerMethodField(read_only=True)
    featured_posts = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Brand
        fields = ('company_name',  'website', 'description','brand_files','file_ids','profile_image','id','featured_posts')

    def get_profile_image(self,obj):
        try:
            profile_str = str(obj.user.profile_image)
            if AWS_S3_CUSTOM_DOMAIN in profile_str:
                return str(obj.user.profile_image)
            else:
                return obj.user.profile_image.url
        except Exception as e:
            return ''

    def get_featured_posts(self, obj):
        try:
            MEDIA_URL = settings.MEDIA_URL

            campaign_list = CampaignMedia.objects.filter(campaign__user__id=obj.user_id).annotate(
                media_file__media_file=Concat(Value(MEDIA_URL),'media_file__media_file', output_field=CharField() ))
            campaign_list = list(campaign_list.values('media_file__media_file',
                                                      'media_file__file_type'))

            return campaign_list
        except Exception as e:
            raise e
            return []    


class AgencySerializer(serializers.ModelSerializer):
    agency_files = AgencyMediaSerializer(many=True,read_only=True)
    file_ids = serializers.ListField(child=serializers.IntegerField(), required=False)
    featured_posts = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = Agency
        fields = ('agency_name', 'website', 'description','agency_files','file_ids','featured_posts')

    def get_featured_posts(self, obj):
        try:
            MEDIA_URL = settings.MEDIA_URL

            campaign_list = CampaignMedia.objects.filter(campaign__user__id=obj.user_id).annotate(
                media_file__media_file=Concat(Value(MEDIA_URL),'media_file__media_file', output_field=CharField() ))
            campaign_list = list(campaign_list.values('media_file__media_file',
                                                      'media_file__file_type'))

            return campaign_list
        except Exception as e:
            raise e
            return []  

class UserListSerializer(serializers.ModelSerializer):
    age = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'phone', 'gender', 'date_of_birth', 'short_bio', 'user_type', 'age',
            'profile_image',
            'facebook', 'instagram','twitter')
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def get_age(self, obj):
        return obj.age_in_years


class CampaignMediaSerializer(serializers.ModelSerializer):
    media_file = HotiMediaSerializer()

    class Meta:
        model = CampaignMedia
        fields = ('id', 'campaign', 'media_file')


class AssociatedBrandSerializer(serializers.ModelSerializer):
    profile_image = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Brand
        fields = ('company_name', 'profile_image','id')

    def get_profile_image(self,obj):
        try:
            profile_str = str(obj.user.profile_image)
            if AWS_S3_CUSTOM_DOMAIN in profile_str:
                return str(obj.user.profile_image)
            else:
                return obj.user.profile_image.url
        except Exception as e:
            return ''



class CampaignSerializer(serializers.ModelSerializer):
    associated_brands = AssociatedBrandSerializer(required=False, read_only=True)
    associated_influencers = serializers.SerializerMethodField()
    content_category = ContentCategorySerializer(many=True, read_only=True)
    campaign_files = CampaignMediaSerializer(many=True, read_only=True)
    start_date = serializers.SerializerMethodField()
    end_date = serializers.SerializerMethodField()
    campaign_period = serializers.SerializerMethodField()

    

    class Meta:
        model = Campaign
        fields = ('campaign_name', 'status', 'description', 'start_date', 'end_date', 'deliverables',
                  'request_brand_for_approval', 'id',  'content_category',
                  'user_id', 'campaign_files','campaign_period','associated_brands','associated_influencers')

    def get_start_date(self, obj):
        try:
            if type(obj.start_date)==str:
                start_date = datetime.strptime(obj.start_date, "%Y-%m-%dT%H:%M:%SZ")
                return datetime.strftime(start_date, "%B, %Y")
            else:
                return datetime.strftime(obj.start_date, "%B, %Y")
        except:
            return ''
    def get_end_date(self, obj):
        try:
            if type(obj.end_date) == str:
                end_date = datetime.strptime(obj.end_date, "%Y-%m-%dT%H:%M:%SZ")
                return datetime.strftime(end_date, "%B, %Y")
            else:
                return datetime.strftime(obj.end_date, "%B, %Y")
        except:
            return ''
    def get_campaign_period(self, obj):
        try:
            output_str = ''
            if obj.status in ['Completed','completed']:
                output_str += convert_datetime_format(obj.start_date, "%B, %Y")
                output_str += '-'+convert_datetime_format(obj.end_date, "%B, %Y")
            elif obj.status in ['Ongoing','ongoing']:
                output_str += convert_datetime_format(obj.start_date, "%B, %Y")
            return output_str
        except:
            return ''

    def get_associated_influencers(self, obj):
        return []




class UserSerializer(serializers.ModelSerializer):
    content_category = ContentCategorySerializer(many=True)
    user_fb = UserFBDetailsSerializer(many=True, required=False, read_only=True)
    campaign = CampaignSerializer(many=True, required=False, read_only=True)
    verified_status = serializers.SerializerMethodField(read_only=True)
    profile_name = serializers.SerializerMethodField()
    profile_image = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id','password','username', 'email', 'phone', 'gender', 'date_of_birth', 'short_bio', 'profile_image', 'first_name',
            'last_name', 'content_category', 'user_type','location',
            'background_image', 'facebook', 'instagram','twitter', 'campaign','age_in_years','user_fb','verified_status','profile_name')
        extra_kwargs = {
            'password': {'write_only': True,'required':True},
            'profile_image': {"required": False, "allow_null": True},
            'email': {'required': True},
            'location':{'required':True}
        }

    def get_verified_status(self, obj):
            return obj.verified_status

    def get_profile_name(self, obj):
        return get_user_name(obj)

    def get_profile_image(self,obj):
        try:
            profile_str=str(obj.profile_image)
            if AWS_S3_CUSTOM_DOMAIN in profile_str:
                return str(obj.profile_image)
            else:
                return obj.profile_image.url
        except Exception as e:
            return ''



class UserInfluencerSerializer(UserSerializer):
    """ Inheriting base user serializer and append influencer serializer """
    influencer = InfluencerSerializer()


    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ('influencer',)

    def create(self, validated_data):
        """
        If user type is influencer this code will execute while serializer.save() gets calling.
        request data has "influencer" key which has data of influencer
        we are storing "influencer" data separately in influencer model
        other than "influencer" data , storing in user table
        """
        user, user_obj = create_user_content(validated_data, 'influencer', Influencer)
        user.influencer = user_obj
        return user
    
    def validate(self, data):
        """
        Ensure that a password is provided when creating a new user.
        """
        if self.instance is None and 'password' not in data:
            raise serializers.ValidationError({'password': 'Password is required.'})
        if self.instance is None and 'first_name' not in data:
            raise serializers.ValidationError({'first_name': 'first_name is required.'})
        if self.instance is None and 'last_name' not in data:
            raise serializers.ValidationError({'last_name': 'last_name is required.'})
        return data
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        if 'username' in data:
            return data
        elif 'first_name' in data and 'last_name' in data:
            data['username'] = f"{data['first_name']} {data['last_name']}"
        else:
            data['username'] = ''
        return data




class UserBrandSerializer(UserSerializer):
    """ Inheriting base user serializer and append brand serializer """
    brand = BrandSerializer()

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ('brand',)

    def create(self, validated_data):
        """
          If user type is brand this code will execute while serializer.save() gets calling.
          request data has "brand" key which has data of brand
          we are storing "brand" data separately in influencer model
          other than "brand" data , storing in user table
          """
        user, user_obj = create_user_content(validated_data, 'brand', Brand, BrandMedia)
        user.brand = user_obj
        return user
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        if 'brand' in data and 'company_name' in data['brand']:
            data['username'] = data['brand']['company_name']
        else:
            if 'first_name' not in data or 'last_name' not in data:
                data['username'] = ''
            elif data['last_name'] is None:
                data['username'] = data['first_name']
            else:
                data['username'] = f"{data['first_name']} {data['last_name']}"
        return data


class UserAgencySerializer(UserSerializer):
    """ Inheriting base user serializer and append agency serializer """
    agency = AgencySerializer()

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ('agency',)

    def create(self, validated_data):
        """
          If user type is agency this code will execute while serializer.save() gets calling.
          request data has "agency" key which has data of brand
          we are storing "agency" data separately in agency model
          other than "agency" data , storing in user table
          """
        user, user_obj = create_user_content(validated_data, 'agency', Agency, AgencyMedia)
        user.agency = user_obj
        return user
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        if 'agency' in data and 'agency_name' in data['agency']:
            data['username'] = data['agency']['agency_name']
        else:
            if 'first_name' not in data or 'last_name' not in data:
                data['username'] = ''
            elif data['last_name'] is None:
                data['username'] = data['first_name']
            else:
                data['username'] = f"{data['first_name']} {data['last_name']}"
        return data



class UserProfileImageSerializer(serializers.ModelSerializer):
    """
    @note: This serializer for handling profile image of user
    """

    class Meta:
        model = User
        fields = ['profile_image', 'background_image', 'id']


class SocialSerializer(serializers.Serializer):
    """
    Serializer which accepts an OAuth2 access token and provider.
    """
    provider = serializers.CharField(max_length=255, required=True)
    access_token = serializers.CharField(max_length=4096, required=True, trim_whitespace=True)


class DashboardSerializer(serializers.ModelSerializer):
    is_bookmarked = serializers.SerializerMethodField()
    content_category = ContentCategorySerializer(many=True)
    profile_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'profile_image', 'is_bookmarked', 'profile_name', 'content_category', 'user_type','username')

    def get_is_bookmarked(self, obj):
        user_id = self.context['request'].user.id
        has_books = BookmarkedUsers.objects.filter(user_id=user_id, bookmarked_user_id=obj.id).exists()
        return 'Yes' if has_books else 'No'
        
    def get_profile_image(self, obj):
        profile_image = obj.profile_image
        if profile_image is None:
            return "https://hoti.s3.amazonaws.com/media/default_images/userstatic.png"
        else:
            return profile_image

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if representation['profile_image'] is None:
            representation['profile_image'] = "https://hoti.s3.amazonaws.com/media/default_images/userstatic.png"
        return representation
          
    def get_profile_name(self, obj):
        return get_user_name(obj)
    
    def get_user_name(self, obj):
        return get_user_name(obj)




    
class UserMetaSerializer(serializers.ModelSerializer):
    agency_brand_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'username', 'first_name',
            'last_name', 'user_type','agency_brand_name',
        )

    def get_agency_brand_name(self, obj):
        if obj.user_type == 'agency':
            try:
                return obj.agency.agency_name
            except :
                return None
        if obj.user_type == 'brand':
            try:
                return obj.brand.company_name
            except :
                return None



from .models import ContentCategory
class UserWishListItemsSerializer(serializers.ModelSerializer):
    content_category = serializers.SerializerMethodField(read_only=True)
    username = serializers.SerializerMethodField(read_only=True)
    full_name = serializers.SerializerMethodField(read_only=True)
    user_type = serializers.SerializerMethodField(read_only=True)
    profile_image = serializers.SerializerMethodField(read_only=True)
    facebook = serializers.SerializerMethodField(read_only=True)
    instagram = serializers.SerializerMethodField(read_only=True)
    twitter = serializers.SerializerMethodField(read_only=True)
    profile_name = serializers.SerializerMethodField(read_only=True)


    class Meta:
        model = UserWishListItems
        fields = ('id', 'user', 'user_wish_list', 'username', 'profile_name','full_name', 'user_type', 'profile_image',
                  'facebook', 'instagram', 'content_category','twitter')
        
    def get_profile_image(self, obj):
        profile_image = obj.profile_image
        if profile_image is None:
            return "https://hoti.s3.amazonaws.com/media/default_images/userstatic.png"
        else:
            return profile_image
        
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['content_category'] = self.get_content_category(instance)
        
        if representation['profile_image'] is None:
            representation['profile_image'] = "https://hoti.s3.amazonaws.com/media/default_images/userstatic.png"
        
        return representation

    # def to_representation(self, instance):
    #     representation = super().to_representation(instance)
    #     if representation['profile_image'] is None:
    #         representation['profile_image'] = "https://hoti.s3.amazonaws.com/media/default_images/userstatic.png"
    #     return representation    

    # def to_representation(self, instance):
    #     data = super().to_representation(instance)
    #     data['content_category'] = self.get_content_category(instance)
    #     return data
        
    def get_profile_name(self, obj):
        f_name = obj.user.first_name if obj.user.first_name is not None else ''
        l_name = obj.user.last_name if obj.user.last_name is not None else ''
        return str(f_name) + ' ' + str(l_name)    

    def get_content_category(self, obj):
        content_categories = obj.user.content_category.all()
        if content_categories:
            data = {}
            for category in content_categories:
                content_category = category.content_category
                id = category
            
            return [{"content_category": category.content_category} for category in content_categories]
        else:
            return []


    def get_username(self, obj):
        return obj.user.username

    def get_full_name(self, obj):
        f_name = obj.user.first_name if obj.user.first_name is not None else ''
        l_name = obj.user.last_name if obj.user.last_name is not None else ''
        return str(f_name) + ' ' + str(l_name)

    def get_user_type(self, obj):
        return obj.user.user_type

    def get_profile_image(self, obj):
        if obj.user.profile_image:
            profile_str = str(obj.user.profile_image)
            if AWS_S3_CUSTOM_DOMAIN in profile_str:
                return str(obj.user.profile_image)
            else:
                return obj.user.profile_image.url
        else:
            return None

    def get_facebook(self, obj):
        return obj.user.facebook if obj.user.facebook else None

    def get_instagram(self, obj):
        return obj.user.instagram if obj.user.instagram else None
    def get_twitter(self, obj):
        return obj.user.twitter if obj.user.twitter else None




class UserWishListSerializer(serializers.ModelSerializer):
    user_wish_list_items = UserWishListItemsSerializer(many=True, read_only=True)
    share_list_id = serializers.SerializerMethodField( read_only=True)
    profile_name = serializers.SerializerMethodField(read_only=True)
    profile_image = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = UserWishList
        fields = ('id', 'list_name','user_wish_list_items','share_list_id','profile_name','profile_image')

    def get_share_list_id(self,obj):
        try:
            return obj.id
        except:
            return None

    def get_profile_image(self, obj):
        try:
            return obj.user.profile_image.decode('utf-8', errors='ignore')
        except:
            return None
    def get_profile_name(self, obj):
        f_name = obj.user.first_name if obj.user.first_name is not None else ''
        l_name = obj.user.last_name if obj.user.last_name is not None else ''
        return str(f_name) + ' ' + str(l_name)

class ManyUploadFileSerializer(serializers.Serializer):
    media_files = serializers.ListField(child=serializers.FileField())


    def create(self, validated_data):
        """
        Create and return a list of `HotiMedia` instances, given the validated data.
        """
        files_data = validated_data.pop('media_files')
        hoti_media_list = []
        for file_data in files_data:
            hoti_media = HotiMedia.objects.create(media_file=file_data)
            data_dict = model_to_dict(hoti_media)
            data_dict['media_file'] = data_dict['media_file'].url
            hoti_media_list.append(data_dict)
        return hoti_media_list


class ChangePasswordSerializer(serializers.Serializer):
    model = User

    """
    Serializer for password change endpoint.
    """
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

class ForgetPasswordSerializer(serializers.Serializer):
    model = User

    """
    Serializer for password change endpoint.
    """
    otp = serializers.CharField(required=True)
    email = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

class EmailResetSerializer(serializers.Serializer):
    model=User
    email=serializers.CharField(required=True)
    otp=serializers.CharField(required=True)
    new_email=serializers.CharField(required=True)

class UserFullNameMetaSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ('full_name',)


# class UserWishListByShareIdSerializer(serializers.ModelSerializer):
#     user_wish_list_items = UserWishListItemsSerializer(many=True, read_only=True)
#     share_list_id = serializers.SerializerMethodField( read_only=True)
#     profile_name = serializers.SerializerMethodField(read_only=True)
#     profile_image = serializers.SerializerMethodField(read_only=True)
    
#     class Meta:
#         model = UserWishList
#         fields = ('id', 'list_name','user_wish_list_items','share_list_id','profile_name','profile_image')

#     def get_share_list_id(self,obj):
#         return obj.id

#     def get_profile_image(self, obj):
#         try:
#             return obj.user.profile_image.decode('utf-8', errors='ignore')
#         except:
#             return None
#     def get_profile_name(self, obj):
#         f_name = obj.user.first_name if obj.user.first_name is not None else ''
#         l_name = obj.user.last_name if obj.user.last_name is not None else ''
#         return str(f_name) + ' ' + str(l_name)
from rest_framework.response import Response
class UserWishListByShareIdSerializer(serializers.ModelSerializer):
    user_wish_list_items = UserWishListItemsSerializer(many=True, read_only=True)
    share_list_id = serializers.SerializerMethodField(read_only=True)
    profile_name = serializers.SerializerMethodField(read_only=True)
    profile_image = serializers.SerializerMethodField(read_only=True)
    agency_name = serializers.SerializerMethodField(read_only=True)
    agency_profile_image = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = UserWishList
        fields = ('id', 'list_name', 'user_wish_list_items', 'share_list_id', 'profile_name', 'profile_image', 'agency_name', 'agency_profile_image')

    
    def get_share_list_id(self, obj):
        return obj.id



    def get_profile_image(self, obj):
        try:
            return obj.user.profile_image.decode('utf-8', errors='ignore')
        except:
            return None

    def get_profile_name(self, obj):
        f_name = obj.user.first_name if obj.user.first_name is not None else ''
        l_name = obj.user.last_name if obj.user.last_name is not None else ''
        return str(f_name) + ' ' + str(l_name)

    def get_agency_name(self, obj):
        try:
            agency = Agency.objects.get(user=obj.user)
            return agency.agency_name
        except Agency.DoesNotExist:
            return None

    def get_agency_profile_image(self, obj):
        try:
            agency = Agency.objects.get(user=obj.user)

            if agency.user.profile_image:
                profile_str = str(agency.user.profile_image)
                if AWS_S3_CUSTOM_DOMAIN in profile_str:
                    return str(agency.user.profile_image)
                else:
                    return agency.user.profile_image.url
            else:
                return None
        except Agency.DoesNotExist:
            return None





class DashboardProfileSearchSerializer(serializers.ModelSerializer):

    profile_image = serializers.SerializerMethodField(read_only=True)
    profile_name = serializers.SerializerMethodField(read_only=True)
    content_category = ContentCategorySerializer(many=True)

    class Meta:
        model = User
        fields = ('profile_name', 'username','profile_image', 'user_type', 'id','username','instagram', 'twitter','facebook','content_category')

    def to_representation(self, instance):
        representation=super().to_representation(instance)
        if representation['profile_image'] is None:
            representation['profile_image']="https://hoti.s3.amazonaws.com/media/default_images/userstatic.png"
        return representation   
    
    def get_profile_image(self,obj):
        if obj.profile_image:
            profile_str = str(obj.profile_image)
            if AWS_S3_CUSTOM_DOMAIN in profile_str:
                return str(obj.profile_image)
            else:
                return obj.profile_image.url
        else:
                return "https://hoti.s3.amazonaws.com/media/default_images/userstatic.png"
    
    def get_profile_name(self, obj):
        return get_user_name(obj)

