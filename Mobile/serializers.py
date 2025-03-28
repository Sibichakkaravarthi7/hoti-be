from django.forms import model_to_dict
from rest_framework import serializers
from master.serializers import ContentCategorySerializer
from accounts.serializers import create_user_content
from accounts.serializers import UserFBDetailsSerializer,CampaignSerializer,UserSerializer,InfluencerSerializer,BrandSerializer,AgencySerializer
from accounts.models import User, BookmarkedUsers, HotiMedia,Influencer
import base64
import uuid
from django import forms
from django.core.files.base import ContentFile

class mobileUserInfluencerSerializer(UserSerializer):
    """ Inheriting base user serializer and append influencer serializer """
    influencer = InfluencerSerializer()

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields +  ('influencer',)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        influencer_data = representation.pop('influencer', {})
        representation.update(influencer_data)
        return representation 
    
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
    
    # def to_representation(self, instance):
    #     data = super().to_representation(instance)
    #     if 'username' in data:
    #         return data
    #     elif 'first_name' in data and 'last_name' in data:
    #         data['username'] = f"{data['first_name']} {data['last_name']}"
    #     else:
    #         data['username'] = ''
    #     return data
       

class mobileUserBrandSerializer(UserSerializer):
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
        representation = super().to_representation(instance)
        influencer_data = representation.pop('brand', {})
        representation.update(influencer_data)
        return representation     

class mobileUserAgencySerializer(UserSerializer):
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
        representation = super().to_representation(instance)
        influencer_data = representation.pop('agency', {})
        representation.update(influencer_data)
        return representation      

class mobileEmailResetSerializer(serializers.Serializer):
    model=User
    email=serializers.CharField(required=True)
    otp=serializers.CharField(required=True)
    new_email=serializers.CharField(required=True)

class mobileUserSerializer(serializers.ModelSerializer):
    content_category = ContentCategorySerializer(many=True)
    user_fb = UserFBDetailsSerializer(many=True, required=False, read_only=True)
    campaign = CampaignSerializer(many=True, required=False, read_only=True)
    verified_status = serializers.SerializerMethodField(read_only=True)
    profile_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id','password','username', 'email', 'phone', 'gender', 'short_bio', 'profile_image', 'first_name',
            'last_name', 'content_category', 'user_type','location',
            'background_image','campaign','age_in_years','user_fb','verified_status','profile_name')
        extra_kwargs = {
            'password': {'write_only': True,'required':True},
            'profile_image': {"required": False, "allow_null": True},
            'email': {'required': True},
            'location':{'required':True}
        }

    def get_verified_status(self, obj):
            return obj.verified_status

    def get_profile_name(self, obj):
        if obj.user_type == 'agency':
            try:
                return obj.agency.agency_name
            except :
                return None
        elif obj.user_type == 'brand':
            try:
                return obj.brand.company_name
            except :
                return None
        else:
            f_name = obj.first_name if obj.first_name is not None else ''
            l_name = obj.last_name if obj.last_name is not None else ''
            return str(f_name) + ' ' + str(l_name)

class mobileDashboardSerializer(serializers.ModelSerializer):
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

    def get_profile_name(self, obj):
        f_name = obj.first_name if obj.first_name is not None else ''
        l_name = obj.last_name if obj.last_name is not None else ''
        return str(f_name) + ' ' + str(l_name)
    
class mobileUserListSerializer(serializers.ModelSerializer):
    age = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'phone', 'gender','location','date_of_birth', 'short_bio', 'user_type', 'age',
            'profile_image',
            'facebook', 'instagram','background_image','content_category')
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def get_age(self, obj):
        return obj.age_in_years


class MobileUploadVideoSerializer(serializers.Serializer):
    uri = serializers.FileField(write_only=True)

    def create(self, validated_data):
        media_file = validated_data.pop('uri')
        hoti_media = HotiMedia.objects.create(media_file=media_file)
        data_dict = model_to_dict(hoti_media)
        data_dict['media_file'] = data_dict['media_file'].url
        return data_dict
    
class MobileUploadFileSerializer(serializers.Serializer):
    base_64_data = serializers.CharField(write_only=True)
    type = serializers.CharField(write_only=True)

    def create(self, validated_data):
        """
        Create and return a list of `HotiMedia` instances, given the validated data.
        """
        base_64_data = validated_data.pop('base_64_data')
        file_extension_type = validated_data.pop('type')
        try:
            file_extension = file_extension_type.split('/')[-1]
        except:
            if file_extension_type in ['video/mp4']:
                file_extension='mp4'
            else:
                file_extension = 'jpeg'

        file_name = f"{uuid.uuid4()}.{file_extension}"
        # Decode and save the file
        decoded_data = base64.b64decode(base_64_data)
        file = ContentFile(decoded_data, name=file_name)
        hoti_media = HotiMedia.objects.create(media_file=file)
        data_dict = model_to_dict(hoti_media)
        data_dict['media_file'] = data_dict['media_file'].url
        return data_dict


class DashboardProfileSearchSerializer(serializers.ModelSerializer):

    profile_image = serializers.SerializerMethodField(read_only=True)
    profile_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ('profile_name', 'username','profile_image', 'user_type', 'id')

    def get_profile_image(self, obj):
        try:
            return obj.profile_image.url
        except Exception as e:
            return ''

    def get_profile_name(self, obj):
        if obj.user_type == 'agency':
            try:
                return obj.agency.agency_name
            except :
                return None
        elif obj.user_type == 'brand':
            try:
                return obj.brand.company_name
            except :
                return None
        else:
            f_name = obj.first_name if obj.first_name is not None else ''
            l_name = obj.last_name if obj.last_name is not None else ''
            return str(f_name) + ' ' + str(l_name)