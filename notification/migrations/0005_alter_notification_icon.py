# Generated by Django 4.1.3 on 2023-03-21 01:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notification', '0004_alter_notification_icon'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='icon',
            field=models.CharField(blank=True, choices=[('exclamation-diamond-fill', 'exclamation-diamond-fill'), ('exclamation-diamond', 'exclamation-diamond'), ('exclamation-triangle-fill', 'exclamation-triangle-fill'), ('exclamation-triangle', 'exclamation-triangle'), ('envelope-exclamation-fill', 'envelope-exclamation-fill'), ('envelope-exclamation', 'envelope-exclamation'), ('person-fill-exclamation', 'person-fill-exclamation'), ('person-fill-exclamation-fill', 'person-fill-exclamation-fill'), ('database-fill-exclamation', 'database-fill-exclamation'), ('database-exclamation', 'database-exclamation'), ('arrow-repeat', 'arrow-repeat'), ('award-fill', 'award-fill'), ('award', 'award'), ('bell-fill', 'bell-fill'), ('bell', 'bell'), ('cart-check-fill', 'cart-check-fill'), ('cart-check', 'cart-check'), ('cart-dash-fill', 'cart-dash-fill'), ('cart-dash', 'cart-dash'), ('cart-plus-fill', 'cart-plus-fill'), ('cart-plus', 'cart-plus'), ('download', 'download'), ('envelope-at-fill', 'envelope-at-fill'), ('envelope-at', 'envelope-at'), ('filetype-xls', 'filetype-xls'), ('filetype-csv', 'filetype-csv'), ('geo-alt-fill', 'geo-alt-fill'), ('geo-alt', 'geo-alt')], default='bell-fill', max_length=55, null=True),
        ),
    ]
