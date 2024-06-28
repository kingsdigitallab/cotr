# from django.conf import settings
from django.contrib import admin
from django.urls import path
from django.views.generic import TemplateView
from .views import view_api_regions, view_api_regions_compare, \
    view_api_regions_all_plaintext

admin.autodiscover()

urlpatterns = [
    path(
        'regions/',
        TemplateView.as_view(template_name='ctrs_lab/lab_regions.html'),
        name='lab_regions'
    ),
    path(
        'api/regions/compare/',
        view_api_regions_compare,
        name='lab_api_regions_compare'
    ),
    path(
        'api/regions/',
        view_api_regions,
        name='lab_api_regions'
    ),
    path(
        'api/regions/all/plaintext/',
        view_api_regions_all_plaintext,
    )
]
