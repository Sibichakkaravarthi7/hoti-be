"""
URL configuration for influencer project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from rest_framework.authtoken.views import obtain_auth_token
from accounts.views import UserListCreateView
from accounts.views import CustomObtainAuthToken, LogoutAPIView
from accounts.views import CreateUserAPIView, UserProfileImageView
from django.contrib.auth import views as auth_views

from accounts.views import FBClass,InstaClass
from django.views.generic import TemplateView


from admindashboard import views as adminviews

urlpatterns = [
    path('admin/', admin.site.urls),
# path('rest-auth/', include('rest_auth.urls')),
#     path('api-auth/', include('rest_framework.urls')),
    path('master/', include('master.urls')),
    path('mobile/',include('Mobile.urls')),
    path('accounts/', include('accounts.urls')),
    path('admin-dashboard/', include('admindashboard.urls')),
    path('api-token-auth/', obtain_auth_token, name='api_token_auth'),
    path('users/', UserListCreateView.as_view(), name='user_list_create'),
    path('custom-auth/', CustomObtainAuthToken.as_view(), name='custom_auth'),
    path('users/create/', CreateUserAPIView.as_view(), name='create_user'),
    path('users/upload-image/', UserProfileImageView.as_view(), name='upload_image'),
path('rest-auth/facebook/', FBClass.as_view(), name='fb_loginnew'),
path('api/insta/',InstaClass.as_view(),name='instgram'),
    # path('facebook-auth/callback/', FacebookAuthCallbackView.as_view(), name='facebook_callback'),
    path('', TemplateView.as_view(template_name='index.html'), name='home'),
# path('oauth/login/', SocialLoginView.as_view())

    path('login/', adminviews.login_view, name='login'),


    path('verify/', adminviews.home_view, name='verify'),


    path('logout/', adminviews.logout_view, name='logout'),

    path('perform-action/', adminviews.perform_action, name='perform_action'),

path('api/logout/', LogoutAPIView.as_view(), name='logout'),

]
