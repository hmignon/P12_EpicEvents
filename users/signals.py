def populate_models(sender, **kwargs):
    from .models import User

    User.objects.get_or_create(
        username='admin',
        email='admin@email.com',
        password='epicevents',
    )
