from rest_framework import serializers

from foodcartapp.models import Product, ProductCategory, Order, OrderItem


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['name', 'category', 'image', 'special_status', 'description', 'price']


class ProductCategorySerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True, read_only=True)
    class Meta:
        model = ProductCategory
        fields = ['name']


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['order', 'product', 'quantity']


class OrderSerializer(serializers.ModelSerializer):
    products = OrderItemSerializer(many=True, read_only=True)
    class Meta:
        model = Order
        fields = ['firstname', 'lastname', 'phonenumber', 'address']
