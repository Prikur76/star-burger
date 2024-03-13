from rest_framework import serializers

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
    products = OrderItemSerializer(many=True, allow_empty=False)
    class Meta:
        model = Order
        fields = ['products', 'firstname', 'lastname', 'phonenumber', 'address']
