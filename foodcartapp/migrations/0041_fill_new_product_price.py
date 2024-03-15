from django.db import migrations


def change_product_price(apps, schema_editor):
    order_products = apps.get_model('foodcartapp', 'OrderItem')
    order_products_for_update = order_products.objects.select_related('product').filter(price__isnull=True)
    for order_product in order_products_for_update.iterator():
        order_product.price = order_product.product.price
        order_product.save()


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0040_orderitem_price'),
    ]

    operations = [
        migrations.RunPython(change_product_price)
    ]
