# Generated by Django 3.2.15 on 2024-03-15 14:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0042_auto_20240315_1631'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='comment',
            field=models.TextField(blank=True, verbose_name='комментарий'),
        ),
    ]
