# Generated by Django 2.0 on 2018-08-10 16:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0006_peoplepage'),
    ]

    operations = [
        migrations.RenameField(
            model_name='peoplepage',
            old_name='name',
            new_name='job_title',
        ),
    ]
