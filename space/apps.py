from django.apps import AppConfig


class RoomConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'space'

    def ready(self) -> None:
        from . import signals
        return super().ready()