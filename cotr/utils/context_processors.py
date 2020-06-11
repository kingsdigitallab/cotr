from django.conf import settings


def settings_context(_request):
    return {
        "settings": settings,
        # temporary fix as {{ settings.WAGTAIL_SITE_NAME }} doesn't work from templates
        "WAGTAIL_SITE_NAME": settings.WAGTAIL_SITE_NAME,
    }
