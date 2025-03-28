
from django.contrib import admin
from django.urls import path, include

from .views import MasterListView, ContentCategoryAddView, ContentCategoryUpdateView, ContentCategoryDeleteView

urlpatterns = [
    path('get-master-list/', MasterListView.as_view(), name='get_master_list_data'),
    path('content-category/add/', ContentCategoryAddView.as_view(), name='content-category-add'),
    path('content-category/<int:id>/update/', ContentCategoryUpdateView.as_view(), name='content-category-update'),
    path('content-category/<int:id>/delete/', ContentCategoryDeleteView.as_view(), name='content-category-delete'),

]
