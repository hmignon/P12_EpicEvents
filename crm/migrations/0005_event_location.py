# Generated by Django 4.0.2 on 2022-02-27 11:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0004_alter_contract_client_alter_event_contract_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='location',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]