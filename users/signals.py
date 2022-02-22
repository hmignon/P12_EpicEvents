def populate_models(sender, **kwargs):
    from django.contrib.auth.models import Group
    from django.contrib.auth.models import Permission
    from .models import User

    try:
        Group.objects.get(name='SALES')
    except Group.DoesNotExist:
        sales = Group.objects.create(name='SALES')
        sales.permissions.set([1, 2, 4, 6, 8, 9])

    try:
        Group.objects.get(name='SUPPORT')
    except Group.DoesNotExist:
        support = Group.objects.create(name='SUPPORT')
        support.permissions.set([4, 10, 12])

    try:
        Group.objects.get(name='MANAGEMENT')
    except Group.DoesNotExist:
        management = Group.objects.create(name='MANAGEMENT')
        management.permissions.set([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])

    User.objects.get_or_create(
        username='admin',
        email='admin@email.com',
        password='epicevents',
        is_staff=True,
        is_superuser=True
    )
