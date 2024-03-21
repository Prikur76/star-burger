from django import forms
from django.shortcuts import redirect, render
from django.views import View
from django.urls import reverse_lazy
from django.db.models import F, Sum
from django.contrib.auth.decorators import user_passes_test
from geopy import distance

from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views


from foodcartapp.models import Product, Restaurant, Order
from foodcartapp.api.serializers import OrderViewSerializer


class Login(forms.Form):
    username = forms.CharField(
        label='Логин', max_length=75, required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Укажите имя пользователя'
        })
    )
    password = forms.CharField(
        label='Пароль', max_length=75, required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        })
    )


class LoginView(View):
    def get(self, request, *args, **kwargs):
        form = Login()
        return render(request, "login.html", context={
            'form': form
        })

    def post(self, request):
        form = Login(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                if user.is_staff:  # FIXME replace with specific permission
                    return redirect("restaurateur:RestaurantView")
                return redirect("start_page")

        return render(request, "login.html", context={
            'form': form,
            'ivalid': True,
        })


class LogoutView(auth_views.LogoutView):
    next_page = reverse_lazy('restaurateur:login')


def is_manager(user):
    return user.is_staff  # FIXME replace with specific permission


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_products(request):
    restaurants = list(Restaurant.objects.order_by('name'))
    products = list(Product.objects.prefetch_related('menu_items'))

    products_with_restaurant_availability = []
    for product in products:
        availability = {item.restaurant_id: item.availability for item in product.menu_items.all()}
        ordered_availability = [availability.get(restaurant.id, False) for restaurant in restaurants]

        products_with_restaurant_availability.append(
            (product, ordered_availability)
        )

    return render(request, template_name="products_list.html", context={
        'products_with_restaurant_availability': products_with_restaurant_availability,
        'restaurants': restaurants,
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_restaurants(request):
    return render(request, template_name="restaurants_list.html", context={
        'restaurants': Restaurant.objects.all(),
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_orders(request):
    orders = list(
        OrderViewSerializer(
            Order.objects.total_cost().exclude(status='COMPLETED'),
            many=True
        ).data)

    for order in orders:
        if order['available_restaurants']:
            order_latitude = order['available_restaurants'][0]['latitude']
            order_longitude = order['available_restaurants'][0]['longitude']
            restaurant_latitude = linked_restaurant.get('latitude', False)
            restaurant_longitude = linked_restaurant.get('longitude', False)
            linked_restaurant['distance'] = None
            if order_longitude and order_latitude and restaurant_latitude and restaurant_longitude:
                linked_restaurant['distance'] = distance.distance(
                    (order_latitude, order_longitude),
                    (restaurant_latitude, restaurant_longitude)
                    ).km
            order['available_restaurants'] = sorted(order['available_restaurants'], key=lambda x: x['distance'])
    return render(
        request,
        template_name='order_items.html',
        context={
            'order_items': orders,
            'current_url': request.path
        }
    )
