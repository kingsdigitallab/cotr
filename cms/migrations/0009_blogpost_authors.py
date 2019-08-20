# Generated by Django 2.2.3 on 2019-08-20 14:16

from django.conf import settings
from django.db import migrations
import modelcluster.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('cms', '0008_table_block'),
    ]

    operations = [
        migrations.AddField(
            model_name='blogpost',
            name='authors',
            field=modelcluster.fields.ParentalManyToManyField(blank=True, null=True, related_name='authored_blogposts', to=settings.AUTH_USER_MODEL, verbose_name='authors'),
        ),
    ]
