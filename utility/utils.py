import requests
from utility import utilconstants as nc
from restservice.models import *
import hashlib
from django.core.exceptions import ObjectDoesNotExist

"""
File for general utility functions and classes.
"""

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


def get_food(food_name):
    """
    Makes a request to get info for a certain food.
    :param food_name: The name of the food
    :return: A FoodCacheRecord
    """

    try:
        food_obj = FoodCache.objects.get(food_hash=md5_hash_string(food_name))
    except ObjectDoesNotExist:
        food_cache_dict = food_request(food_name)
        food_obj = FoodCache.objects.create(
            food_hash=food_cache_dict["food_hash"],
            food_name=food_cache_dict["food_name"],
            kilocalories=food_cache_dict["kilocalories"],
            fat_grams=food_cache_dict["fat_grams"],
            carb_grams=food_cache_dict["carb_grams"],
            protein_grams=food_cache_dict["protein_grams"]
        )

    return food_obj


def food_request(food_name):
    # Make request to Nutritics
    r = requests.get(build_food_req_string(food_name), auth=(nc.NUTRITICS_USER, nc.NUTRITICS_PSWD))

    response = r.json()
    if response["status"] != 200:
        raise RuntimeError("Nutritics query failed")

    food_hash = md5_hash_string(food_name)
    food_data = response["1"]

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


def md5_hash_string(string):
    """
    Returns a Hex representation of running an MD5 hash on the given string.
    :param string: String to hash
    :return: Hex hash string
    """
    return hashlib.md5(string.encode()).hexdigest()


def calories_from_macros(carb, fat, protein):
    return (fat*9) + ((carb+protein)*4)
