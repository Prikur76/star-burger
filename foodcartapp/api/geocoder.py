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


def get_distance_km(apikey, order):
    """
    Returns distance between order and restaurants
    """
    if order.get('available_restaurants'):
        order_lon, order_lat = fetch_coordinates(apikey, order.get('address'))
        for restaurant in order.get('available_restaurants'):
            restaurant_lon, restaurant_lat = fetch_coordinates(apikey, restaurant.get('address'))
            restaurant['distance'] = round(distance((order_lat, order_lon), (restaurant_lat, restaurant_lon)).km, 2)
        order['available_restaurants'] = sorted(order.get('available_restaurants'), key=lambda x: x['distance'])
    return order
