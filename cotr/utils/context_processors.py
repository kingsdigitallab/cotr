from django.conf import settings


def settings_context(_request):
    return {
        # TODO: check if ds is actually used
        # better not to send all the settings params to template
        'ds': {k: getattr(settings, k) for k in settings.FRONT_END_SETTINGS},
    }
