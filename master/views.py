from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import IsSuperUser
# Create your views here.
from .models import ContentCategory
from .serializers import ContentCategorySerializer, InterestSerializer
class MasterListView(APIView):
    def get(self, request):
        content_category_queryset = ContentCategory.objects.all()
        insterest_queryset = ContentCategory.objects.all()

        content_category_serializer = ContentCategorySerializer(content_category_queryset, many=True)
        insterest_serializer = InterestSerializer(insterest_queryset, many=True)

        data = {'content_category': content_category_serializer.data,
                 'insterest': insterest_serializer.data,
               }


        return Response(data)


class ContentCategoryAddView(generics.CreateAPIView):
    queryset = ContentCategory.objects.all()
    serializer_class = ContentCategorySerializer
    permission_classes = [IsAuthenticated,IsSuperUser]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, updated_by=self.request.user)

class ContentCategoryUpdateView(generics.UpdateAPIView):
    queryset = ContentCategory.objects.all()
    serializer_class = ContentCategorySerializer
    lookup_field = 'id'
    permission_classes = [IsAuthenticated,IsSuperUser]

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

class ContentCategoryDeleteView(generics.DestroyAPIView):
    queryset = ContentCategory.objects.all()
    serializer_class = ContentCategorySerializer
    lookup_field = 'id'
    permission_classes = [IsAuthenticated,IsSuperUser]

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({'detail': 'Content category successfully deleted.'}, status=status.HTTP_200_OK)
