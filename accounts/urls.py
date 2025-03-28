


from django.contrib import admin
from django.urls import path, include

from accounts.dashboard import UserSearchView, UserSearchMetaView, UserBrandDetailsByIdView, UserAgencyDetailsByIdView, \
    UserInfluencerDetailsByIdView, UserProfileSearchMetaView, UserProfileSearchView, LocationCitySearchMetaView
from accounts.otp import SendOTP, VerifyOTP, VerifyEmailAndSendOTP,  VerifyOTPAndChangePassword ,VerifyAndChangeEmail
from accounts.views import AllTypeOfUserListView, InfluencerUserDetailView, \
    InfluencerUpdateAPIView, CampaignCreateAPIView, UploadFileView, CampaignListAPIView, UserDetailView, \
    UserDetailByIdAPIView, UserTypeListAPIView, UserWishListCreateView, UserWishListView, UserWishListItemsAPIView, \
    UserUpdateAPIView, UserWishListItemsDeleteView, UserWishListDeleteView, UserWishListRenameView, ChangePasswordView, \
    UserWishListByShareListIdView,CampaignDeleteView

urlpatterns = [
    path('listusers/', AllTypeOfUserListView.as_view(), name='AllTypeOfUserListView'),

    path('get-userlist-meta-by-type/<str:user_type>/', UserTypeListAPIView.as_view(), name='user-meta'),
    path('user-detail/', UserDetailView.as_view(), name='user-detail'),
    path('user-detail-by-id/<int:user_id>/', UserDetailByIdAPIView.as_view(), name='user-detail-id'),
    path('user-brand-detail-by-id/<int:user_id>/', UserBrandDetailsByIdView.as_view(), name='user-brand-detail-id'),
    path('user-agency-detail-by-id/<int:user_id>/', UserAgencyDetailsByIdView.as_view(), name='user-agency-detail-id'),
    path('user-influencer-detail-by-id/<int:user_id>/', UserInfluencerDetailsByIdView.as_view(), name='user-influencer-detail-id'),

    path('influencer-update/<int:user_id>/', InfluencerUpdateAPIView.as_view(), name='influencer-update'),

    path('user-update/', UserUpdateAPIView.as_view(), name='user-update'),

    path('campaigns/', CampaignCreateAPIView.as_view(), name='campaign-list-create'),

    path('upload-file/', UploadFileView.as_view(), name='upload_file'),
    path('campaignlist/', CampaignListAPIView.as_view(), name='capaign-list'),

    path('createwishlist/', UserWishListCreateView.as_view(), name='create-wish-list'),
    path('wishlist/', UserWishListView.as_view(), name='wish-list'),
    path('wishlist-by-list-id/<int:share_list_id>/', UserWishListByShareListIdView.as_view(), name='wish-list-by-list-id'),
    path('wishlistitems/', UserWishListItemsAPIView.as_view(), name='wish-list-items'),
    path('renamewishlist/',UserWishListRenameView.as_view(),name='rename-wish-list'),
    path('deletewishlistitems/',UserWishListItemsDeleteView.as_view(),name='delete-wish-list-items'),
    path('deletewishlist/',UserWishListDeleteView.as_view(),name='delete-wish-list'),
    path('users-search/<str:user_type>/', UserSearchView.as_view(), name='user-search'),
    path('city-search/', LocationCitySearchMetaView.as_view(), name='city-search'),
    path('users-profile-search/<str:user_type>/', UserProfileSearchView.as_view(), name='user-search'),

    path('users-meta-search/<str:user_type>/', UserSearchMetaView.as_view(), name='user-meta-search'),
    path('users-profile-meta-search/<str:user_type>/<str:search_str>', UserProfileSearchMetaView.as_view(), name='user-profile-meta-search'),

    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('send-email-otp/', SendOTP.as_view(), name='send-email-otp'),
    path('verify-email-otp/', VerifyOTP.as_view(), name='verify-email-otp'),
    path('verify-email-send-otp/', VerifyEmailAndSendOTP.as_view(), name='verify-email-send-otp'),
    path('verify-otp-change-password/', VerifyOTPAndChangePassword.as_view(), name='verify-otp-change-password'),
    path('campaign-delete/',CampaignDeleteView.as_view(),name='delete_campaign'),
    path('verify-otp-change-email/',VerifyAndChangeEmail.as_view(),name='verify-otp-change-email')



]
