import sys

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

PLUGIN_NAME = "care_sast"

BUILD_TIME_COMMANDS = {
    "collectstatic",
    "makemigrations",
    "migrate",
    "compilemessages",
    "makemessages",
    "spectacular",
    "test",
}


class Care_sastConfig(AppConfig):
    name = PLUGIN_NAME
    verbose_name = _("CARE SAST")

    def ready(self):
        if len(sys.argv) > 1 and sys.argv[1] in BUILD_TIME_COMMANDS:
            return

        from care_sast.settings import plugin_settings

        plugin_settings.validate()
