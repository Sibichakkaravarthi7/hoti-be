from rest_framework import serializers
from master.models import ContentCategory


class ContentCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentCategory
        fields =['id', 'content_category']

class InterestSerializer(serializers.ModelSerializer):
    interest_name = serializers.CharField(source='content_category')

    class Meta:
        model = ContentCategory
        fields =['id', 'interest_name']