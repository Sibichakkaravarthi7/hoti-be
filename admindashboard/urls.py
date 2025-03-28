
from django.contrib import admin
from django.urls import path, include

import admindashboard.views as adminviews


urlpatterns = [
    path('home-admin/',adminviews.CountSummaryAPIView.as_view(),name='home-admin'),
    path('agency-list/', adminviews.AdminAgencyListView.as_view(), name='agency-list'),
    path('brand-list/', adminviews.AdminBrandListView.as_view(), name='brand-list'),
    path('influencer-list/', adminviews.AdminInfluncerListView.as_view(), name='influencer-list'),
    path('update-verify-status/<int:user_id>', adminviews.UpdateUserVerifiedStatus.as_view(), name='update-verify-status'),
    path('update-verify-status-all-backend/', adminviews.UpdateVerifiedToALLByAPI.as_view(), name='update-verify-status-all'),
    ]
