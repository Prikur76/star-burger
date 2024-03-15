from rest_framework import serializers
from django.db import transaction

from foodcartapp.models import Product, ProductCategory, Order, OrderItem


class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = ['id', 'name']


class ProductSerializer(serializers.ModelSerializer):
    category = ProductCategorySerializer()
    class Meta:
        model = Product
        fields = ['id', 'name', 'category', 'image', 'special_status', 'description', 'price']


class OrderItemSerializer(serializers.ModelSerializer):

    def validate_quantity(self, quantity):
        if quantity <= 0:
            raise serializers.ValidationError('Количество должно быть больше нуля')
        return quantity

    class Meta:
        model = OrderItem
        fields = ['product', 'quantity']


class OrderSerializer(serializers.ModelSerializer):
    products = OrderItemSerializer(many=True, allow_empty=False, write_only=True)

    def create(self, validated_data):
        products = validated_data.pop('products')
        with transaction.atomic():
            order = Order.objects.create(**validated_data)
            needed_products = [product['product'] for product in products]
            order_products = [OrderItem(order=order, **product) for product in products]
            for num, order_product in enumerate(order_products):
                order_product.price = needed_products[num].price
            OrderItem.objects.bulk_create(order_products)
            return order

    class Meta:
        model = Order
        fields = ['products', 'firstname', 'lastname', 'phonenumber', 'address']
