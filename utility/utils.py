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
    def __init__(self, meal_name, user):
        self.user = user
        self.meal_name = meal_name
        self.carb = 0
        self.protein = 0
        self.fat = 0
        # Generates a meal ID using the MD5 hash, based on the name of the meal and the user's ID
        self.meal_id = md5_hash_string(meal_name + user.user_id)

    def add_food(self, food_name, serving_size=0):
        """
        Adds a Food to the meal, and updates meal macros accordingly
        :param food_name: The name of the food to add
        :param serving_size: The serving size to scale the food to. If left unchanged (default 0)
                then the default serving size for the user is used
        """
        food = get_food(food_name)

        # Get scale factor
        if serving_size == 0:
            scale = self.user.serving_size / 100
        else:
            scale = serving_size / 100

        # Apply scaling
        self.protein += food.protein_grams * scale
        self.carb += food.carb_grams * scale
        self.fat += food.fat_grams * scale

        # Convert floats to ints
        self.protein = int(round(self.protein))
        self.fat = int(round(self.fat))
        self.carb = int(round(self.carb))

    def generate_meal_record(self):
        """
        Construct and return a MealCache object
        :return: A MealCache object that represents this meal
        """
        meal = MealCache.objects.create(
            meal_id=self.meal_id,
            meal_name=self.meal_name,
            user_id=self.user.user_id,
            fat_grams=self.fat,
            protein_grams=self.protein,
            carb_grams=self.carb,
            kilocalories=calories_from_macros(self.carb, self.fat, self.protein)
        )
        return meal


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
