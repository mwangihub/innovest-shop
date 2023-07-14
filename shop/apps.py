from django.apps import AppConfig


class EcommerceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'shop'

    def ready(self):
        import shop.signals  # noqa
        from shop.signals import PostOrderOrdered
        PostOrderOrdered.handle_post_order_ordered

