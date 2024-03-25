from django.db import transaction
from rest_framework import serializers

from addresses.models import Place
from foodcartapp.models import Product, ProductCategory
from foodcartapp.models import Order, OrderItem
from foodcartapp.models import Restaurant
from .geocoder import fetch_coordinates


class RestaurantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = ["name", "address", "contact_phone"]


class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = ["id", "name"]


class ProductSerializer(serializers.ModelSerializer):
    category = ProductCategorySerializer()

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "category",
            "image",
            "special_status",
            "description",
            "price",
        ]


class OrderItemSerializer(serializers.ModelSerializer):

    def validate_quantity(self, quantity):
        if quantity <= 0:
            raise serializers.ValidationError(
                "Количество должно быть больше нуля"
            )
        return quantity

    class Meta:
        model = OrderItem
        fields = ["product", "quantity"]


class OrderSerializer(serializers.ModelSerializer):
    products = OrderItemSerializer(many=True, allow_empty=False)

    def create(self, validated_data):
        products = validated_data.pop("products")
        with transaction.atomic():
            order = Order.objects.create(**validated_data)
            needed_products = [product["product"] for product in products]
            order_products = [
                OrderItem(order=order, **product) for product in products
            ]
            for num, order_product in enumerate(order_products):
                order_product.price = needed_products[num].price
            OrderItem.objects.bulk_create(order_products)
            order_address = order.address
            if not Place.objects.filter(address=order_address).exists():
                order_coordinates = fetch_coordinates(order_address)
                if not order_coordinates:
                    order_place = Place.objects.create(address=order_address)
                order_place = Place.objects.create(
                    address=order_address,
                    longitude=order_coordinates[1],
                    latitude=order_coordinates[0],
                )
                order_place.save()
            return order

    class Meta:
        model = Order
        fields = [
            "products",
            "firstname",
            "lastname",
            "phonenumber",
            "address"
        ]


class OrderViewSerializer(serializers.ModelSerializer):
    cost = serializers.IntegerField(read_only=True)
    order_status = serializers.CharField(
        source="get_status_display", read_only=True)
    payment_method_name = serializers.CharField(
        source="get_payment_method_display", read_only=True
    )
    available_restaurants = RestaurantSerializer(
        source="get_available_restaurants", many=True, read_only=True
    )
    linked_restaurant = RestaurantSerializer(
        source="restaurant", read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "firstname",
            "lastname",
            "phonenumber",
            "address",
            "status",
            "order_status",
            "payment_method",
            "payment_method_name",
            "cost",
            "comment",
            "available_restaurants",
            "linked_restaurant",
            "registered_at",
            "called_at",
            "delivered_at",
        ]
        read_only_fields = ["status"]
