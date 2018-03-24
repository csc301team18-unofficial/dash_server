import requests
from nutrition import nutriconstants as nc
from restservice.models import *
import hashlib
from django.core.exceptions import ObjectDoesNotExist


class MealBuilder:
    """
    Container / utility class that represents a meal that the user is trying to log.
    A meal is made up of multiple food objects.
    """
    def __init__(self, name):
        self.name = name
        self.k_cal = 0
        self.carb = 0
        self.protein = 0
        self.fat = 0
        # Generates a meal ID using the MD5 hash, based on the name of the meal
        self.meal_id = md5_hash_string(name)

    def add_food(self, food):
        """
        Adds a Food to the meal, and updates meal macros accordingly
        :param food: A Food object
        """
        self.k_cal += food.k_cal
        self.protein += food.protein
        self.carb += food.carb
        self.fat += food.fat

    def generate_meal_record(self, ):
        # TODO: Create MealEntry record
        pass


class NutriHandler:
    """
    Utility class used to make API calls for a particular client.
    """
    def __init__(self, default_serving_size=100):
        """
        :param default_serving_size: Default serving size for any food object that's generated. Used to scale Nutritics
                    data. Defaults to 100 (for getFoodInfo requests)
        """
        self.client_default_serve_size = default_serving_size

    def get_food(self, food_name):
        """
        Makes a request to get info for a certain food.
        TODO: Can potentially throw a RuntimeException, handle in the parent call
        :param food_name: The name of the food
        :return: A FoodCacheRecord
        """

        try:
            food_obj = FoodCache.objects.get(food_hash=md5_hash_string(food_name))
        except ObjectDoesNotExist:
            food_obj = FoodCache.objects.create(self.food_request(food_name))
            
        return food_obj

    def food_request(self, food_name):
        # Make request to Nutritics
        r = requests.get(build_food_req_string(food_name), auth=(nc.NUTRITICS_USER, nc.NUTRITICS_PSWD))
        if r.status_code != 200:
            # There's been an error with the get request, so the operation fails
            raise RuntimeError("Nutritics request failed with status code {}".format(r.status_code))

        food_hash = md5_hash_string(food_name)
        food_data = r.json()["1"]

        food_cache_dict = dict(
            food_hash=food_hash,
            food_name=food_name,
            kilocalories=food_data["energyKcal"]["val"],
            protein_grams=food_data["protein"]["val"],
            carb_grams=food_data["carbohydrate"]["val"],
            fat_grams=food_data["fat"]["val"]
        )

        return food_cache_dict


def build_food_req_string(food_name):
    """
    Build a request URL to get a single-item list from Nutritics for a food, with all macros for that food.
    :param food_name: The name of the food we're searching for
    :return: The URL to set the GET request to
    """
    reqstr = nc.FOOD_BASE_URL + food_name + nc.ALL_ATTRS + nc.LIMIT_ONE
    return reqstr


def md5_hash_string(str):
    """
    Returns a Hex representation of running an MD5 hash on the given string.
    :param str: String to hash
    :return: Hex hash string
    """
    return hashlib.md5(str.encode()).hexdigest()
