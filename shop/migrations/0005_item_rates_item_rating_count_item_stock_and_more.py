# Generated by Django 4.1 on 2022-09-09 18:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0004_alter_address_options_alter_address_address_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='rates',
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name='item',
            name='rating_count',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='item',
            name='stock',
            field=models.PositiveIntegerField(default=5),
        ),
        migrations.AlterField(
            model_name='order',
            name='ordered_date',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
