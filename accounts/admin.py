from django.contrib import admin
from accounts.models import User,Influencer,Brand,Agency,SocialMediaData,BookmarkedUsers,Campaign,HotiMedia,CampaignMedia,UserWishList,UserWishListItems

# from django.contrib.auth.admin import UserAdmin
# # Register your models here.
admin.site.register(User)
admin.site.register(Influencer)

