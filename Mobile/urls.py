from django.contrib import admin
from django.urls import path, include
from accounts.dashboard import UserSearchView, UserSearchMetaView, UserBrandDetailsByIdView, UserAgencyDetailsByIdView, \
    UserInfluencerDetailsByIdView, UserProfileSearchMetaView, UserProfileSearchView
from Mobile.otp import mobileSendOTP, mobileVerifyOTP, mobileVerifyEmailAndSendOTP,  mobileVerifyOTPAndChangePassword,mobileVerifyAndChangeEmail
from Mobile.views import mobileAllTypeOfUserListView, mobileInfluencerUserDetailView, \
    mobileInfluencerUpdateAPIView, mobileCampaignCreateAPIView, mobileUploadFileView, mobileCampaignListAPIView, \
    mobileUserDetailView, mobileCampaignDeleteView, \
    mobileUserDetailByIdAPIView, mobileUserTypeListAPIView, mobileUserWishListCreateView, mobileUserWishListView, \
    mobileUserWishListItemsAPIView, \
    mobileUserUpdateAPIView, mobileUserWishListItemsDeleteView, mobileUserWishListDeleteView, \
    mobileUserWishListRenameView, mobileChangePasswordView, \
    mobileUserWishListByShareListIdView, mobileCustomObtainAuthToken, mobileUserListCreateView, mobileCreateUserAPIView, \
    mobileUserProfileImageView, \
    mobileFBClass, mobileLogoutAPIView, MobileUploadFileView, VideoForm, upload_video
from Mobile.dashboard import mobileUserProfileSearchMetaView,mobileUserProfileSearchView,mobileUserSearchMetaView


from admindashboard import views as adminviews
urlpatterns = [
    path('mobile-listusers/', mobileAllTypeOfUserListView.as_view(), name='AllTypeOfUserListView'),
    path('mobile-custom-auth/', mobileCustomObtainAuthToken.as_view(), name='custom_auth'),
    path('mobile-users/', mobileUserListCreateView.as_view(), name='user_list_create'),
    path('mobile-get-userlist-meta-by-type/<str:user_type>/', mobileUserTypeListAPIView.as_view(), name='user-meta'),
    path('mobile-user-detail/', mobileUserDetailView.as_view(), name='user-detail'),

    path('mobile-user-detail-by-id/<int:user_id>/', mobileUserDetailByIdAPIView.as_view(), name='user-detail-id'),
    path('mobile-user-brand-detail-by-id/<int:user_id>/', UserBrandDetailsByIdView.as_view(), name='user-brand-detail-id'),
    path('mobile-user-agency-detail-by-id/<int:user_id>/', UserAgencyDetailsByIdView.as_view(), name='user-agency-detail-id'),
    path('mobile-user-influencer-detail-by-id/<int:user_id>/', UserInfluencerDetailsByIdView.as_view(), name='user-influencer-detail-id'),
    path('mobile-influencer-update/<int:user_id>/', mobileInfluencerUpdateAPIView.as_view(), name='influencer-update'),

    path('mobile-user-update/', mobileUserUpdateAPIView.as_view(), name='user-update'),
    path('mobile-campaigns/', mobileCampaignCreateAPIView.as_view(), name='campaign-list-create'),
    path('mobile-upload-file/', mobileUploadFileView.as_view(), name='upload_file'),
    path('mobile-campaignlist/', mobileCampaignListAPIView.as_view(), name='capaign-list'),
    path('mobile-createwishlist/', mobileUserWishListCreateView.as_view(), name='create-wish-list'),

    path('mobile-wishlist/', mobileUserWishListView.as_view(), name='wish-list'),
    path('mobile-wishlist-by-list-id/<int:share_list_id>/', mobileUserWishListByShareListIdView.as_view(), name='wish-list-by-list-id'),
    path('mobile-wishlistitems/', mobileUserWishListItemsAPIView.as_view(), name='wish-list-items'),
    path('mobile-renamewishlist/',mobileUserWishListRenameView.as_view(),name='rename-wish-list'),
    path('mobile-deletewishlistitems/',mobileUserWishListItemsDeleteView.as_view(),name='delete-wish-list-items'),

    path('mobile-deletewishlist/',mobileUserWishListDeleteView.as_view(),name='delete-wish-list'),
    path('mobile-users-profile-search/<str:user_type>/', mobileUserProfileSearchView.as_view(), name='user-search'),
    path('mobile-users-meta-search/<str:user_type>/', mobileUserSearchMetaView.as_view(), name='user-meta-search'),
    path('mobile-users-profile-meta-search/<str:user_type>/<str:search_str>/', mobileUserProfileSearchMetaView.as_view(), name='user-profile-meta-search'),

    path('mobile-change-password/', mobileChangePasswordView.as_view(), name='change-password'),
    path('mobile-send-email-otp/',  mobileSendOTP.as_view(), name='send-email-otp'),
    path('mobile-verify-email-otp/',  mobileVerifyOTP.as_view(), name='verify-email-otp'),
    path('mobile-verify-email-send-otp/',  mobileVerifyEmailAndSendOTP.as_view(), name='verify-email-send-otp'),
    path('mobile-verify-otp-change-password/',  mobileVerifyOTPAndChangePassword.as_view(), name='verify-otp-change-password'),

    path('mobile-users/create/', mobileCreateUserAPIView.as_view(), name='create_user'),
    path('mobile-users/upload-image/', mobileUserProfileImageView.as_view(), name='upload_image'),
    path('mobile-rest-auth/facebook/', mobileFBClass.as_view(), name='fb_loginnew'),
    path('mobile-file-upload/', MobileUploadFileView.as_view(), name='mobile-file-upload'),
    path('mobile-test-upload/', upload_video, name='test-file-upload'),
    path('mobile-campaign-delete/',mobileCampaignDeleteView.as_view(),name='delete_campaign'),
    path('mobile-verify-otp-change-email/',mobileVerifyAndChangeEmail.as_view(),name='verify-otp-change-email')

    # # path('', mobileTemplateView.as_view(template_name='index.html'), name='home'),
    # path('mobilelogin/', adminviews.login_view, name='login'),
    # path('mobileverify/', adminviews.home_view, name='verify'),
    # path('mobilelogout/', adminviews.logout_view, name='logout'),

    # path('mobileperform-action/', adminviews.perform_action, name='perform_action'),
    # path('mobileapi/logout/', mobileLogoutAPIView.as_view(), name='logout'),



]

