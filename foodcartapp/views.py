import json

from django.http import JsonResponse
from django.templatetags.static import static

from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Product, Order, OrderItem

# @api_view(['POST'])
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

# @api_view(['POST'])
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
    return JsonResponse(dumped_products, safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })

@api_view(['POST'])
def register_order(request):
    form_content = request.data
    # print(form_content)

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

    order = Order.objects.get_or_create(
        first_name=form_content.get('firstname'),
        last_name=form_content.get('lastname'),
        phonenumber=form_content.get('phonenumber'),
        address=form_content.get('address')
    )[0]
    products = Product.objects.all()
    for product in form_content.get('products'):
        order_item = OrderItem.objects.create(
            order=order,
            product=products.get(id=product.get('product')),
            quantity=product.get('quantity')
        )

    return Response({'order_id': order.id}, status=200)
