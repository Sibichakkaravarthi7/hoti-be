# Generated by Django 3.2 on 2023-05-12 15:39

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0001_initial'),
        ('master', '0001_initial'),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.AddField(
            model_name='influencer',
            name='interests',
            field=models.ManyToManyField(blank=True, null=True, to='master.Interest'),
        ),
        migrations.AddField(
            model_name='influencer',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='influencer', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='campaignmedia',
            name='campaign',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='campaign_files', to='accounts.campaign'),
        ),
        migrations.AddField(
            model_name='campaignmedia',
            name='media_file',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='hoti_campaign_files', to='accounts.hotimedia'),
        ),
        migrations.AddField(
            model_name='campaign',
            name='associated_brands',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='campaign_brand', to='accounts.brand'),
        ),
        migrations.AddField(
            model_name='campaign',
            name='associated_influencers',
            field=models.ManyToManyField(blank=True, null=True, to='accounts.Influencer'),
        ),
        migrations.AddField(
            model_name='campaign',
            name='content_category',
            field=models.ManyToManyField(blank=True, null=True, to='master.ContentCategory'),
        ),
        migrations.AddField(
            model_name='campaign',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='campaign', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='brandmedia',
            name='brand',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='brand_files', to='accounts.brand'),
        ),
        migrations.AddField(
            model_name='brandmedia',
            name='media_file',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='hoti_brand_files', to='accounts.hotimedia'),
        ),
        migrations.AddField(
            model_name='brand',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='brand', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='bookmarkedusers',
            name='bookmarked_user_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bookmarked_user', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='bookmarkedusers',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bookmarked_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='agencymedia',
            name='agency',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='agency_files', to='accounts.agency'),
        ),
        migrations.AddField(
            model_name='agencymedia',
            name='media_file',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='hoti_agency_files', to='accounts.hotimedia'),
        ),
        migrations.AddField(
            model_name='agency',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='agency', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='user',
            name='content_category',
            field=models.ManyToManyField(blank=True, null=True, related_name='user_content', to='master.ContentCategory'),
        ),
        migrations.AddField(
            model_name='user',
            name='groups',
            field=models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups'),
        ),
        migrations.AddField(
            model_name='user',
            name='user_permissions',
            field=models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions'),
        ),
        migrations.AlterUniqueTogether(
            name='userwishlistitems',
            unique_together={('user', 'user_wish_list')},
        ),
        migrations.AlterUniqueTogether(
            name='userwishlist',
            unique_together={('user', 'list_name')},
        ),
    ]
