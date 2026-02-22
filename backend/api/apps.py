from django.apps import AppConfig


class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'

    def ready(self):
        # We import here to avoid issues with app registry
        from .keep_alive import start_keep_alive_loop
        start_keep_alive_loop()
