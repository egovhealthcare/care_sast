from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

PLUGIN_NAME = "care_sast"


class Care_sastConfig(AppConfig):
    name = PLUGIN_NAME
    verbose_name = _("CARE SAST")

    def ready(self):
        pass
