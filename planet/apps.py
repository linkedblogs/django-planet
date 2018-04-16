from django.apps import AppConfig

class PlanetConfig(AppConfig):
    name = "planet"
    verbose_name = "django feed aggregator"

    def ready(self):
        from planet.models import delete_asociated_tags
        from django.db.models.signals import pre_delete
        model = self.get_model('Post')
        pre_delete.connect(delete_asociated_tags, sender=model)
        import planet.signals
