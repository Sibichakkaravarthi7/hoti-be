from django.db import models # type: ignore

from django.conf import settings # type: ignore

class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # created_by = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='%(app_label)s_%(class)s_created_by')
    # updated_by = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='%(app_label)s_%(class)s_updated_by')

    class Meta:
        abstract = True

# Create your models here.
# class Interest(BaseModel):
#     interest_name = models.CharField(max_length=50)
#     created_by = models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True, on_delete=models.DO_NOTHING, related_name='create_interest_categories')
#     updated_by = models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True, on_delete=models.DO_NOTHING, related_name='updated_interest_categories')
#
#     def __str__(self):
#         return self.interest_name


class ContentCategory(BaseModel):
    content_category = models.CharField(max_length=50)
    created_by = models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True, on_delete=models.DO_NOTHING,related_name='create_content_categories')
    updated_by = models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True, on_delete=models.DO_NOTHING, related_name='updated_content_categories')

    def __str__(self):
        return self.content_category
