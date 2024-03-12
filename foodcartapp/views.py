import json
import re

from django.http import JsonResponse
from django.templatetags.static import static

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.serializers import ValidationError

from .models import Product, Order, OrderItem
from .api.serializers import (
    ProductSerializer,
    OrderSerializer,
    OrderItemSerializer
)


def banners_list_api(request):
    # FIXME move data to db?
    return JsonResponse([
        {
            'title': 'Burger',
            'src': static('burger.jpg'),
            'text': 'Tasty Burger at your door step',
        },
        {
            'title': 'Spices',
            'src': static('food.jpg'),
            'text': 'All Cuisines',
        },
        {
            'title': 'New York',
            'src': static('tasty.jpg'),
            'text': 'Food is incomplete without a tasty dessert',
        }
    ], safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


@api_view(['GET', 'POST'])
def product_list_api(request):
    products = Product.objects.select_related('category').available()

    dumped_products = []
    for product in products:
        dumped_product = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'special_status': product.special_status,
            'description': product.description,
            'category': {
                'id': product.category.id,
                'name': product.category.name,
            } if product.category else None,
            'image': product.image.url,
            'restaurant': {
                'id': product.id,
                'name': product.name,
            }
        }
        dumped_products.append(dumped_product)
    return Response(dumped_products)


def validate_order(request):
    pass



@api_view(['POST'])
def register_order(request):
    form_content = request.data

    # Firstname field
    if 'firstname' not in form_content:
        return Response(
            data={'error': 'the firstname field is empty or not represented'},
            status=400
        )
    if not form_content['firstname']:
        return Response(
            data={'error': 'firstname key empty or not presented'},
            status=400
        )
    if not isinstance(form_content['firstname'], str):
        return Response(
            data={'error': 'wrong type of the firstname field'},
            status=400
        )

    # Lastname field
    if 'lastname' not in form_content:
        return Response(
            data={'error': 'the lastname field is empty or not represented'},
            status=400
        )
    if not form_content['lastname']:
        return Response(
            data={'error': 'lastname key empty or not presented'},
            status=400
        )
    if not isinstance(form_content['lastname'], str):
        return Response(
            data={'error': 'wrong type of the lastname field'},
            status=400
        )

    # Phonenumber field
    if 'phonenumber' not in form_content:
        return Response(
            data={'error': 'the phonenumber field is empty or not represented'},
            status=400
        )
    if not form_content['phonenumber']:
        return Response(
            data={'error': 'phonenumber key empty or not presented'},
            status=400
        )
    if not isinstance(form_content['phonenumber'], str):
        return Response(
            data={'error': 'wrong type of the phonenumber field'},
            status=400
        )
    if not bool(re.match(r'^\+79|79|89\d{9}$', form_content['phonenumber'])):
        return Response(
            data={'error': 'wrong type of the phonenumber field'},
            status=400
        )

    # Address field
    if 'address' not in form_content:
        return Response(
            data={'error': 'the address field is empty or not represented'},
            status=400
        )
    if not form_content['address']:
        return Response(
            data={'error': 'address key empty or not presented'},
            status=400
        )
    if not isinstance(form_content['address'], str):
        return Response(
            data={'error': 'wrong type of the address field'},
            status=400
        )
    # Products field
    if 'products' not in form_content:
        return Response(
                data={'error': 'the products field is empty or not represented'},
                status=400
        )
    if not form_content['products']:
        return Response(
            data={'error': 'the products field is empty or not represented'},
            status=400
        )
    if not isinstance(form_content['products'], list):
        return Response(
            data={'error': 'wrong type of the products field'},
            status=400
        )
    products = Product.objects.all()
    for product in form_content['products']:
        if 'product' not in product:
            return Response(
                data={'error': 'the product field is empty or not represented'},
                status=400
            )
        if 'quantity' not in product:
            return Response(
                data={'error': 'the quantity field is empty or not represented'},
                status=400
            )

        if not isinstance(product['product'], int):
            return Response(
                data={'error': 'wrong type of the product field'},
                status=400
            )
        if not isinstance(product['quantity'], int):
            return Response(
                data={'error': 'wrong type of the quantity field'},
                status=400
            )

        if not products.filter(id=product['product']).exists():
            return Response(
                data={'error': 'wrong product id'},
                status=400
            )

    order = Order.objects.get_or_create(
        first_name=form_content.get('firstname'),
        last_name=form_content.get('lastname'),
        phonenumber=form_content.get('phonenumber'),
        address=form_content.get('address')
    )[0]

    for product in form_content.get('products'):
        order_item = OrderItem.objects.create(
            order=order,
            product=products.get(id=product.get('product')),
            quantity=product.get('quantity')
        )

    return Response({'order_id': order.id}, status=200)
