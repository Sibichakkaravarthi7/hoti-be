from django.contrib.auth.models import AbstractUser
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.gis.db import models as gis_models

from enum import Enum
from datetime import date
from master.models import  ContentCategory, BaseModel
from datetime import datetime
from django.db.models import JSONField


class Gender(Enum):
    MALE = 'M'
    FEMALE = 'F'
    OTHER = 'O'


GENDER_CHOICES = (
    ('Male', 'Male'),
    ('Female', 'Female'),
    ('Others', 'Others'),
)

VERIFIED_STATUS = (
    ('UnVerified', 'UnVerified'),
    ('Verified', 'Verified'),
    ('Rejected', 'Rejected'),
)

USER_TYPES = (
    ('influencer', 'influencer'),
    ('brand', 'brand'),
    ('agency', 'agency'),
)

CAMPAIGN_STATUS = (
    ('Ongoing', 'Ongoing'),
    ('Completed', 'Completed'),
)


def generate_profile_image_path(instance, filename):
    """
    Returns the upload path for the profile image
    """
    'user/profile_images/'
    return f'user/{instance.id}/profile_images/{filename}'


def generate_background_image_path(instance, filename):
    """
    Returns the upload path for the profile image
    """
    'user/profile_images/'
    return f'user/{instance.id}/background_images/{filename}'


def generate_campaign_image_path(instance, filename):
    """
    Returns the upload path for the profile image
    """
    'user/profile_images/'
    datetime_str = str(datetime.now()).replace('-', '_').replace(':', '_').replace(' ', '_').replace('.', '_')
    return f'campaign/media/{datetime_str}_{filename}'


def generate_media_file_path(instance, filename):
    """
    Returns the upload path for the profile image
    """
    'user/profile_images/'
    datetime_str = str(datetime.now()).replace('-', '_').replace(':', '_').replace(' ', '_').replace('.', '_')
    path = f'campaign/media/{datetime_str}_{filename}'
    return path


class User(AbstractUser):
    refresh_token = models.CharField(max_length=255, blank=True, null=True)
    phone = PhoneNumberField(null=False, blank=False, unique=True)
    gender = models.CharField(max_length=6, choices=GENDER_CHOICES, null=True, blank=True)
    date_of_birth = models.DateField(default=None, blank=True, null=True)
    short_bio = models.CharField(max_length=200)
    user_type = models.CharField(max_length=10, choices=USER_TYPES, null=False, blank=False)
    # is_influencer = models.BooleanField(null=False, blank=False)
    # is_brand = models.BooleanField(null=False, blank=False)
    # is_agency = models.BooleanField(null=False, blank=False)
    profile_image = models.ImageField(upload_to=generate_profile_image_path, null=False, blank=False,
                                      default='default_images/userstatic.png')
    content_category = models.ManyToManyField(ContentCategory, null=True, blank=True, related_name='user_content')
    first_name = models.CharField(max_length=30, blank=True, null=True)
    last_name = models.CharField(max_length=30, blank=True, null=True)
    background_image = models.ImageField(upload_to=generate_background_image_path, null=True, blank=True)
    facebook = models.CharField(max_length=250, blank=True, null=True)
    twitter = models.CharField(max_length=250, blank=True, null=True)
    instagram = models.CharField(max_length=250, blank=True, null=True)
    location = models.CharField(max_length=250, blank=True, null=True)
    verified_status = models.CharField(max_length=10, choices=VERIFIED_STATUS, null=True, blank=True)

    # youtube = models.CharField(max_length=100, blank=True, null=True)

    @property
    def age_in_years(self):
        try:
            today = date.today()
            delta_in_years = today.year - self.date_of_birth.year
            if (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day):
                delta_in_years -= 1
            return delta_in_years
        except:
            return None

    # @property
    # def social_media_profile(self):
    #     if getattr(self, 'influencer', None):
    #         return {'facebook': self.influencer.facebook, 'youtube': self.influencer.youtube,
    #                 'instagram': self.influencer.instagram}
    #     else:
    #         return {}

    # @property
    # def user_type(self):
    #     """
    #
    #     @return: user type
    #     """
    #     return 'influencer' if self.is_influencer else 'brand' if self.is_brand else 'agency' \
    #         if self.is_agency else None

    @property
    def user_profile_image_if_exists(self):
        """

        @return: s3 image url of user profile image
        """
        val = self.profile_image.url if self.profile_image else None
        return val


class Influencer(models.Model):
    user = models.OneToOneField(User, null=False, blank=False, on_delete=models.CASCADE, related_name='influencer')
    interests = models.ManyToManyField(ContentCategory, null=True, blank=True)
    interests_in_our_news_letter = models.BooleanField(null=True, blank=True)
    fb_access_token = models.CharField(max_length=200, blank=True, null=True)


class Brand(models.Model):
    user = models.OneToOneField(User, null=False, blank=False, on_delete=models.CASCADE, related_name='brand')
    company_name = models.CharField(max_length=100, blank=False, null=False)
    # designation = models.CharField(max_length=100, blank=True, null=True)
    website = models.CharField(max_length=100, blank=False, null=False)
    description = models.CharField(max_length=250, blank=False, null=False)


class Agency(models.Model):
    user = models.OneToOneField(User, null=False, blank=False, on_delete=models.CASCADE, related_name='agency')
    agency_name = models.CharField(max_length=100, blank=False, null=False)
    website = models.CharField(max_length=100, blank=False, null=False)
    description = models.CharField(max_length=250, blank=True, null=True)


class SocialMediaData(models.Model):
    # user = models.OneToOneField(User, null=False, blank=False, on_delete=models.CASCADE, related_name='agency')
    facebook_id = models.CharField(max_length=100, blank=False, null=False)
    name = models.CharField(max_length=100, blank=False, null=False)
    email = models.CharField(max_length=250, blank=False, null=False)
    # location = gis_models.PointField(blank=True, null=True)


class BookmarkedUsers(BaseModel):
    user = models.ForeignKey(User, null=False, blank=False, on_delete=models.CASCADE, related_name='bookmarked_by')
    bookmarked_user_id = models.ForeignKey(User, null=False, blank=False, on_delete=models.CASCADE,
                                           related_name='bookmarked_user')


class Campaign(models.Model):
    user = models.ForeignKey(User, null=False, blank=False, on_delete=models.CASCADE, related_name='campaign')
    campaign_name = models.CharField(max_length=30, blank=False, null=False)
    status = models.CharField(max_length=30, choices=CAMPAIGN_STATUS, blank=True, null=True)
    description = models.CharField(max_length=500, blank=True, null=True)
    content_category = models.ManyToManyField(ContentCategory, null=True, blank=True)
    start_date = models.DateTimeField(blank=False, null=False)
    end_date = models.DateTimeField(null=True, blank=True)
    deliverables = models.CharField(max_length=50, blank=False, null=False)
    associated_brands = models.ForeignKey(Brand, null=False, blank=False, on_delete=models.CASCADE,
                                          related_name='campaign_brand')
    associated_influencers = models.ManyToManyField(Influencer, null=True, blank=True)
    request_brand_for_approval = models.BooleanField(null=True, blank=True)


class HotiMedia(models.Model):
    FILE_TYPES = (
        ('image', 'Image'),
        ('video', 'Video'),
        ('pdf', 'Pdf'),
        ('docx', 'Docx'),
    )
    media_file = models.FileField(upload_to=generate_media_file_path, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    file_type = models.CharField(max_length=10, choices=FILE_TYPES, null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.media_file:
            if self.media_file.name.endswith('.mp4'):
                self.file_type = 'video'
            elif self.media_file.name.endswith('.pdf'):
                self.file_type = 'pdf'
            elif self.media_file.name.endswith('.docx'):
                self.file_type = 'docx'
            else:
                self.file_type = 'image'
        super().save(*args, **kwargs)

    @property
    def media_file_url(self):
        if self.media_file:
            return self.media_file.url
        return ''


class CampaignMedia(models.Model):
    campaign = models.ForeignKey(Campaign, related_name='campaign_files', on_delete=models.CASCADE)
    media_file = models.ForeignKey(HotiMedia, related_name='hoti_campaign_files', on_delete=models.CASCADE)


class UserWishList(BaseModel):
    list_name = models.CharField(max_length=50, blank=False, null=False)
    user = models.ForeignKey(User, related_name='wish_list', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'list_name')


class UserWishListItems(BaseModel):
    user = models.ForeignKey(User, related_name='wish_list_items', on_delete=models.CASCADE)
    user_wish_list = models.ForeignKey(UserWishList, related_name='user_wish_list_items', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'user_wish_list')


class AgencyMedia(models.Model):
    agency = models.ForeignKey(Agency, related_name='agency_files', on_delete=models.CASCADE)
    media_file = models.ForeignKey(HotiMedia, related_name='hoti_agency_files', on_delete=models.CASCADE)


class BrandMedia(models.Model):
    brand = models.ForeignKey(Brand, related_name='brand_files', on_delete=models.CASCADE)
    media_file = models.ForeignKey(HotiMedia, related_name='hoti_brand_files', on_delete=models.CASCADE)


class UserFbDetails(BaseModel):
    user = models.ForeignKey(User, related_name='user_fb', on_delete=models.CASCADE)
    no_of_posts = models.IntegerField(blank=True, null=True)
    fb_id = models.CharField(max_length=100, blank=True, null=True)
    fb_name = models.CharField(max_length=200, blank=True, null=True)
    fb_email = models.CharField(max_length=200, blank=True, null=True)
    fb_profile_pic_link = models.CharField(max_length=200, blank=True, null=True)
    data = JSONField()


class UserInstaDetails(models.Model):
    user_id = models.ForeignKey(User, related_name='insta_details', on_delete=models.CASCADE)
    ig_id = models.CharField(max_length=255)
    username = models.CharField(max_length=255)
    followers_count = models.IntegerField(null=True, blank=True)
    media_count = models.IntegerField(null=True, blank=True)
    average_likes = models.FloatField(null=True, blank=True)
    average_comments = models.FloatField(null=True, blank=True)
    average_video_views = models.FloatField(null=True, blank=True)

    # Add any additional fields or methods as needed

    def __str__(self):
        return f"{self.username}'s Instagram Details"


class EmailOTP(models.Model):
    otp = models.IntegerField(null=True, blank=True)
    user = models.ForeignKey(User, related_name='user_otp', on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    email = models.CharField(max_length=250, blank=True, null=True)


class LocationCityMaster(models.Model):
    city_name = models.CharField(max_length=250, blank=False, null=False)
