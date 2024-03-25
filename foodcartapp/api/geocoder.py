import requests
from geopy.distance import distance

from addresses.models import Place
from star_burger.settings import YANDEX_API_KEY


def fetch_coordinates(address):
    """
    Fetches coordinates (latitude and longitude) from the geocoder API
    """
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(
        base_url,
        params={
            "geocode": address,
            "apikey": YANDEX_API_KEY,
            "format": "json",
        },
    )
    response.raise_for_status()
    found_places = response.json()["response"]["GeoObjectCollection"]["featureMember"]

    if not found_places:
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant["GeoObject"]["Point"]["pos"].split(" ")
    return lon, lat


def save_address(address):
    """
    Saves address to the database
    """
    places = Place.objects.all()
    try:
        address = places.get(address=address)
    except Place.DoesNotExist:
        coordinates = fetch_coordinates(address)
        if coordinates:
            address = places.create(
                address=address, longitude=coordinates[1], latitude=coordinates[0]
            )
            address.save()
    return address


def get_distance_km(orders):
    """
    Returns distance between order and restaurants
    """
    orders_addresses = list(
        set(
            [
                order.get("address")
                for order in orders
                if order.get("available_restaurants")
            ]
        )
    )
    restaurant_addresses = list(
        set(
            [
                restaurant.get("address")
                for order in orders
                if order.get("available_restaurants")
                for restaurant in order.get("available_restaurants")
            ]
        )
    )
    orders_addresses.extend(restaurant_addresses)
    for address in orders_addresses:
        save_address(address)
    places = Place.objects.values()
    for order in orders:
        if order.get("available_restaurants"):
            order_coordinates = [
                (place.get("latitude"), place.get("longitude"))
                for place in places
                if place.get("address") == order.get("address")
            ][0]
            for restaurant in order.get("available_restaurants"):
                restaurant_coordinates = [
                    (place.get("latitude"), place.get("longitude"))
                    for place in places
                    if place.get("address") == restaurant.get("address")
                ][0]
                restaurant["distance"] = round(
                    distance(order_coordinates, restaurant_coordinates).km, 2
                )
            order["available_restaurants"] = sorted(
                order.get("available_restaurants"), key=lambda x: x["distance"]
            )
    return orders
