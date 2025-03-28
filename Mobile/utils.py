from accounts.serializers import UserInfluencerSerializer,UserBrandSerializer,UserAgencySerializer
from Mobile.serializers import mobileUserSerializer,mobileUserInfluencerSerializer,mobileUserBrandSerializer,mobileUserAgencySerializer
def mobile_get_user_type_serializer(user):
    print(user.user_type)
    if user.user_type == 'influencer':
        return mobileUserInfluencerSerializer
    elif user.user_type == 'agency':
        return mobileUserAgencySerializer
    elif user.user_type == 'brand':
        return mobileUserBrandSerializer
    else:
        return mobileUserSerializer