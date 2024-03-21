import requests
from geopy.distance import distance


def fetch_coordinates(apikey, address):
    """
    Fetches coordinates (latitude and longitude) from the geocoder API
    """
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(base_url, params={
        "geocode": address,
        "apikey": apikey,
        "format": "json",
    })
    response.raise_for_status()
    found_places = response.json()['response']['GeoObjectCollection']['featureMember']

    if not found_places:
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lon, lat


def get_distance_km(apikey, orders):
    """
    Returns distance between order and restaurants
    """
    for order in orders:
        order_lon, order_lat = fetch_coordinates(apikey, order.get('address'))
        if not order.get('available_restaurants'):
            return orders
        for restaurant in order.get('available_restaurants'):
            if restaurant.get('address'):
                restaurant_lon, restaurant_lat = fetch_coordinates(apikey, restaurant.get('address'))
            if order_lat and order_lon and restaurant_lat and restaurant_lon:
                restaurant['distance'] = round(distance((order_lat, order_lon), (restaurant_lat, restaurant_lon)).km,2)
        order['available_restaurants'] = sorted(order.get('available_restaurants'), key=lambda x: x['distance'])
    return orders
