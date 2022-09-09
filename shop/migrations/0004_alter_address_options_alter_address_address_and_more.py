# Generated by Django 4.0.5 on 2022-08-12 17:07

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('shop', '0003_alter_address_first_name_alter_address_last_name_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='address',
            options={'verbose_name_plural': 'Shipping addresses'},
        ),
        migrations.AlterField(
            model_name='address',
            name='address',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='address',
            name='first_name',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='First name'),
        ),
        migrations.AlterField(
            model_name='address',
            name='last_name',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Second name'),
        ),
        migrations.AlterField(
            model_name='address',
            name='phone',
            field=phonenumber_field.modelfields.PhoneNumberField(blank=True, max_length=128, null=True, region=None),
        ),
        migrations.AlterField(
            model_name='address',
            name='state',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='address',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
    ]
