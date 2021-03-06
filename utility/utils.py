import requests
from utility import utilconstants as nc
from restservice.models import *
import hashlib
import monsterurl
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime, timedelta, time

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

    def create_meal_record(self):
        """
        Construct and return a MealCache object
        :return: A MealCache object that represents this meal
        """
        meal = MealCache.objects.create(
            meal_id=self.meal_id,
            meal_name=self.meal_name,
            user_id=self.user,
            fat_grams=self.fat,
            protein_grams=self.protein,
            carb_grams=self.carb,
            kilocalories=calories_from_macros(self.carb, self.fat, self.protein),
        )
        return meal


def get_meal(user, meal_name):
    """
    Checks the MealCache if the meal exists or not, and return it if it does. If the meal does not exist,
    this function throws an ObjectDoesNotExist Exception that MUST be handled in the parent.
    :param user: The user the meal belongs to
    :param meal_name: The name of the meal
    :return: The named meal object associated to the given user
    """
    meal_id = md5_hash_string(meal_name + user.user_id)
    meal = MealCache.objects.get(meal_id=meal_id)
    return meal


def get_food(food_name):
    """
    Makes a request to get info for a certain food.
    :param food_name: The name of the food
    :return: A FoodCacheRecord
    """
    try:
        food_obj = FoodCache.objects.get(food_id=md5_hash_string(food_name))
    except ObjectDoesNotExist:
        food_cache_dict = food_request(food_name)
        food_obj = FoodCache.objects.create(
            food_id=food_cache_dict["food_id"],
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
        food_id=food_hash,
        food_name=food_name,
        kilocalories=food_data["energyKcal"]["val"],
        protein_grams=food_data["protein"]["val"],
        carb_grams=food_data["carbohydrate"]["val"],
        fat_grams=food_data["fat"]["val"]
    )

    return food_cache_dict


def get_or_create_user_and_goals(client_id):
    """
    NOTE: THIS FUNCTION HAS TO BE CALLED AT THE BEGINNING OF EVERY REQUEST-HANDLING FUNCTION IN THIS CLASS
    THERE ARE NO EXCEPTIONS TO THIS, OR IT'LL BREAK EVERYTHING

    Checks if the client already has a registered account, or if one needs to be made.
    Gets the account if it already exists, or makes a new one if it doesn't.
    """
    try:
        user_entry = Users.objects.get(user_id=client_id)
    except ObjectDoesNotExist:
        user_entry = Users.objects.create(
            user_id=client_id,
            name=monsterurl.get_monster(),
            serving_size=100,
            sprint=1,
            points=0,
            last_checkin=datetime.now()
        )

    try:
        goal_entry = Goals.objects.get(user_id=client_id)
    except ObjectDoesNotExist:
        goal_entry = Goals.objects.create(
            goal_id=md5_hash_string(client_id),
            user_id=user_entry,
            water_ml=3500,
            protein_grams=50,
            fat_grams=70,
            carb_grams=310,
            kilocalories=2070
        )

    return user_entry, goal_entry


def calculate_points(user, user_goals):
    """
    Return the total points awarded to the user for reaching daily goals.
    Points are negative if goals are surpassed.

    The closer the user gets to their goals for today, the more points they're awarded.
    However, if they move past any of their targets, they should be penalised.
    Points and Score are the same thing.

    :param user: The user who's points should be calculated
    :param user_goals: The user's goals

    Workflow:
    User logs a food or meal entry. Entry gets posted into database.
    Points awarded is a function of (todays_macros)/(user_goals)

    todays_macros_dict = dict(
        'carbs_grams' = carbs_g_today,
        'fat_grams' = fat_g_today,
        'protein_grams' = protein_g_today,
        'water_ml' = water_ml_today
    )

    Concrete Example:
    =================
    * Adding points:
    - Total points so far: 150
    - Daily macros so far: 70%
    - Anne logs apple. Apple gets added to Entry
    - Daily macros now: 75%
    - Total points now: 150 + 5 = 155

    * Subtracting points:
    - Total points so far: 150
    - Daily macros so far: 100%
    - Anne logs apple. Apple gets added to Entry
    - Daily macros now: 105%
    - Total points now: 150 - 5 = 145
    """
    try:
        daily_macros_dict = get_today_macros(user, user.last_checkin)

        # if daily amounts consumed are over the goal limit, points are negative

        water_points = daily_macros_dict['water_ml'] / user_goals.water_ml
        water_points = int(water_points*100 if (0 < water_points <= 1) else (-water_points*100))

        protein_points = daily_macros_dict['protein_grams'] / user_goals.protein_grams
        protein_points = int(protein_points*100 if (0 < protein_points <= 1) else (-protein_points*100))

        fat_points = daily_macros_dict['fat_grams'] / user_goals.fat_grams
        fat_points = int(fat_points*100 if (0 < fat_points <= 1) else (-fat_points*100))

        carb_points = daily_macros_dict['carb_grams'] / user_goals.carb_grams
        carb_points = int(carb_points*100 if (0 < carb_points <= 1) else (-carb_points*100))

        points = water_points + protein_points + fat_points + carb_points

        points = points * user.sprint

        return points

    except Exception as e:
        print("CALCULATING POINTS IS BROKEN")
        print(e.__class__.__name__)
        print(e)
        return 10


def get_today_macros(user, start_time=None):
    """
    Get the amount of carbs / protein / fat / water / kcal the user has consumed since the beginning of the day
    :param user: The user we're checking
    :param start_time: The time from which to start checking for entries. If not specified,
    defaults to beginning of the current day
    :return: A dictionary that maps macro -> quantity of macro consumed
    """
    # Food/meal entries logged today so far:

    if start_time:
        start = start_time
        end = start + timedelta(1)
    else:
        start = datetime.now().date()
        end = start + timedelta(1)

    # Macros today:
    carb_g_today = 0
    fat_g_today = 0
    protein_g_today = 0
    water_ml_today = 0
    macros_dict = dict()

    today_start = datetime.combine(start, time())
    today_end = datetime.combine(end, time())

    user_food_list = Entry.objects.filter(user_id=user).filter(time_of_creation__range=[today_start, today_end])

    if user_food_list.exists():
        for entry in user_food_list:
            water_ml_today += entry.water_ml
            carb_g_today += entry.carb_grams
            fat_g_today += entry.fat_grams
            protein_g_today += entry.protein_grams

    macros_dict['kilocalories'] = calories_from_macros(carb_g_today, fat_g_today, protein_g_today)
    macros_dict['carb_grams'] = carb_g_today
    macros_dict['fat_grams'] = fat_g_today
    macros_dict['protein_grams'] = protein_g_today
    macros_dict['water_ml'] = water_ml_today

    return macros_dict


def update_points_sprint_checkin(user, user_goals, current_datetime):
    """
    Rewards the user points, updates their sprint and sets their "last check-in" time.
    :param user: The user who stats are being updated
    :param user_goals: The user's current daily goals
    :param current_datetime: The current date and time (datetime object)
    """

    # update sprint
    update_sprint(user)

    try:
        # update user's last_checkin
        setattr(user, "last_checkin", current_datetime)
    except Exception as e:
        print(e.__class__.__name__)
        print(e)

    try:
        # add points to score
        setattr(user, "points", user.points + calculate_points(user, user_goals))
    except Exception as e:
        print(e.__class__.__name__)
        print(e)

    user.save()


def update_sprint(user):
    """
    Compares the current time with the time in user.last_checkin. If the last check-in was yesterday, increment the
    user's current sprint by 1. If the last check-in was before yesterday, reset the user's sprint to 1.
    Sprint and Streak are the same thing.
    """

    try:
        last_checkin = user.last_checkin
        current_time = datetime.now()
        delta = current_time - last_checkin

        setattr(user, "sprint", (user.sprint+1 if 2 < delta.days < 1 else 1))
        user.save()
    except Exception as e:
        print("UPDATING SPRINT IS BROKEN")
        print(e.__class__.__name__)
        print(e)


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
    """
    Converts quanities of macros in grams into the sum total kilocalorie count
    """
    return (fat * 9) + ((carb + protein) * 4)


def which_meal(datetime_obj):
    """"
    Returns "breakfast", "lunch", or "dinner" classification, given a datetime object.

    On a 24 hour clock,
      Breakfast: 3:00 - 10:59
      Lunch: 11:00 - 15:59
      Dinner: 16:00 - 2:59

    :param: datetime datetime_obj
    :return: string
    """
    # create datetime objects which represent tha bounds of each meal
    # the first three params don't matter since it's year, month, day

    breakfast_time = datetime(1, 1, 1, 3, 0, 0).time()  # breakfast starts at 3am
    lunch_time = datetime(1, 1, 1, 11, 0, 0).time()     # lunch starts at 11am
    dinner_time = datetime(1, 1, 1, 15, 0, 0).time()    # dinner starts at 5pm

    meal_time = datetime_obj.time()
    if breakfast_time <= meal_time < lunch_time:
        return "breakfast_foods"
    elif lunch_time <= meal_time < dinner_time:
        return "lunch_foods"
    else:
        return "dinner_foods"


def get_relevant_user_data(client_name):
    """
    Takes a username and generates a dictionary of information that is relevant to the user.
    This information includes:
        - User's daily goals
        - The number of consecutive days the user has been using DASH
        - User's current calorie count / water consumption / macros / etc
        - User's current score
        - User's current streak
        - A list of foods that the user has consumed today (probably a queryset object or something)

    :param client_name: The client's monstrous username
    :return: Dict of info about the user
    """

    try:
        # Get the user from the database
        user = Users.objects.get(name=client_name)

    except ObjectDoesNotExist:
        # Catch the exception and pass it along, handle in parent
        raise ObjectDoesNotExist

    try:
        user_goals = Goals.objects.get(user_id=user.user_id)
        user_data = dict()
        today_info = get_today_macros(user)

        # Add goals and other stats to user, create space for logged entries
        user_data["username"] = user.name
        user_data["user_score"] = user.points
        user_data["streak"] = user.sprint

        user_data["breakfast_foods"] = []
        user_data["lunch_foods"] = []
        user_data["dinner_foods"] = []

        # Add macro quanities, goals and percentages
        user_data["curr_user_carbs"] = today_info["carb_grams"]
        user_data["user_carbs_goal"] = user_goals.carb_grams
        user_data["user_carbs_percentage"] = int((today_info["carb_grams"] / user_goals.carb_grams) * 100)

        user_data["curr_user_fat"] = today_info["fat_grams"]
        user_data["user_fat_goal"] = user_goals.fat_grams
        user_data["user_fat_percentage"] = int((today_info["fat_grams"] / user_goals.fat_grams) * 100)

        user_data["curr_user_protein"] = today_info["protein_grams"]
        user_data["user_protein_goal"] = user_goals.protein_grams
        user_data["user_protein_percentage"] = int((today_info["protein_grams"] / user_goals.protein_grams) * 100)

        user_data["curr_user_cals"] = today_info["kilocalories"]
        user_data["user_cals_goal"] = user_goals.kilocalories
        user_data["user_cals_percentage"] = int((today_info["kilocalories"] / user_goals.kilocalories) * 100)

        user_data["curr_user_water"] = today_info["water_ml"]
        user_data["user_water_goal"] = user_goals.water_ml
        user_data["user_water_percentage"] = int((today_info["water_ml"] / user_goals.water_ml) * 100)

        if today_info:
            # Add meals and food consumed today is any exist
            start = datetime.now().date()
            end = start + timedelta(1)

            today_start = datetime.combine(start, time())
            today_end = datetime.combine(end, time())

            user_food_list = Entry.objects.filter(user_id=user)\
                .filter(is_water=False)\
                .filter(time_of_creation__range=[today_start, today_end])

            if user_food_list.exists():
                for entry in user_food_list:
                    user_data[which_meal(entry.time_of_creation)].append(entry.entry_name)

        return user_data

    except Exception as e:
        print(e.__class__.__name__)
        print(e)
        raise ObjectDoesNotExist
