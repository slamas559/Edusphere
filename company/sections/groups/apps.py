from django.apps import AppConfig


class GroupsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sections.groups'
    def ready(self):
        import sections.groups.signals  # if you put signals in a separate file
        # or just import your models to register the signals