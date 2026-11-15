from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'

    def ready(self):
        import accounts.signals
        from django.db.models.signals import post_migrate

        post_migrate.connect(accounts.signals.ensure_dev_users, sender=self)
