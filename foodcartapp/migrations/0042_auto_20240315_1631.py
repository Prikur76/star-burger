# Generated by Django 3.2.15 on 2024-03-15 13:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0041_fill_new_product_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('CREATED', 'создан'), ('IN_PROGRESS', 'в обработке'), ('IN_DELIVERY', 'доставляется'), ('COMPLETED', 'завершен')], db_index=True, default='CREATED', max_length=20, verbose_name='статус'),
        ),
        migrations.AddField(
            model_name='order',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='изменен'),
        ),
    ]
