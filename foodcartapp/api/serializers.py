from rest_framework import serializers

from .models import Product, ProductCategory, Order, OrderItem


class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = ['name']


class ProductSerializer(serializers.ModelSerializer):
    category = ProductCategorySerializer(many=False, read_only=True)
    class Meta:
        model = Product
        fields = ['name', 'category', 'image', 'special_status', 'description', 'price']


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['firstname', 'lastname', 'phonenumber', 'address']


class OrderItemSerializer(serializers.ModelSerializer):
    order = OrderSerializer(many=False, read_only=True)
    products = ProductSerializer(many=True)
    class Meta:
        model = OrderItem
        fields = ['order', 'products', 'quantity']

