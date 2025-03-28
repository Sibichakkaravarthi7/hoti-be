from rest_auth import serializers

from accounts.models import User


class AdminUserListSerializer(serializers.ModelSerializer):
    profile_name = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ('id','first_name','last_name','email','date_joined','verified_status',
                  'profile_image', 'profile_name',  'user_type','username')

    def get_profile_name(self, obj):
        f_name = obj.first_name if obj.first_name is not None else ''
        l_name = obj.last_name if obj.last_name is not None else ''
        return str(f_name) + ' ' + str(l_name)

class AdminUserListSerializer(serializers.ModelSerializer):
    profile_name = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ('id','first_name','last_name','email','created_at','verified_status',
                  'profile_image', 'profile_name',  'user_type','username')

    def get_profile_name(self, obj):
        f_name = obj.first_name if obj.first_name is not None else ''
        l_name = obj.last_name if obj.last_name is not None else ''
        return str(f_name) + ' ' + str(l_name)