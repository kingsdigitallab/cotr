# Generated by Django 2.2.10 on 2020-04-16 10:55

from django.db import migrations
from ctrs_texts.utils import get_plain_text


def load_plain(apps, schema_editor):
    EncodedText = apps.get_model('ctrs_texts', 'EncodedText')
    for et in EncodedText.objects.all():
        et.plain = get_plain_text(et)
        et.save()


def unload_plain(apps, schema_editor):
    EncodedText = apps.get_model('ctrs_texts', 'EncodedText')
    for et in EncodedText.objects.all():
        et.plain = ''
        et.save()


class Migration(migrations.Migration):

    dependencies = [
        ('ctrs_texts', '0009_encodedtext_plain'),
    ]

    operations = [
        migrations.RunPython(load_plain, reverse_code=unload_plain),
    ]
