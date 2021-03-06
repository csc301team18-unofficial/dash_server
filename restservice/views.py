from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer

from restservice.serializers import *
from utility.utils import *


class JSONResponse(HttpResponse):
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)


"""
All request handling functions take two parameters: request and client_id

:param request: The request sent by the client
:param client_id: The client's unique ID token (generated by Google). Passed in through the URL and extracted by regex.
"""


@csrf_exempt
def username(request, client_id):
    """
    Get the user's monstrous name! Returns a single item JSON response.

    {
        "name": "AnnoyingAggressiveAardvark"
    }
    """
    if request.method == 'GET':
        user_obj = get_or_create_user_and_goals(client_id)[0]
        response = {"username": user_obj.name}

        return JSONResponse(response, status=status.HTTP_200_OK)

    return HttpResponse(status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
def log_food(request, client_id):
    """
    Gets a JSON object from the client defining the food's name, and optionally the serving size used.
    Logs the food using the specified serving size, or the default serving size

    Update user's points.

    Example JSON request:
    {
        "food_name": "banana",
        "serving": 120
    }

    """
    if request.method == 'POST':
        user, user_goals = get_or_create_user_and_goals(client_id)

        food_entry_json = JSONParser().parse(request)
        if "food_name" in food_entry_json:
            food_name = food_entry_json["food_name"]
            serving = food_entry_json["serving"] if "serving" in food_entry_json else user.serving_size
        else:
            return HttpResponse(status=status.HTTP_400_BAD_REQUEST)

        serving = serving / 100

        food_data = get_food(food_name)

        curr_datetime = datetime.now()

        try:
            # Create food entry
            Entry.objects.create(
                entry_id=md5_hash_string(str(client_id) + str(curr_datetime)),
                user_id=user,
                time_of_creation=curr_datetime,
                entry_name=food_name,
                is_meal=False,
                kilocalories=food_data.kilocalories*serving,
                fat_grams=food_data.fat_grams*serving,
                carb_grams=food_data.carb_grams*serving,
                protein_grams=food_data.protein_grams*serving,
                water_ml=0,
                is_water=False
            )

            update_points_sprint_checkin(user, user_goals, curr_datetime)
            return HttpResponse(status=status.HTTP_200_OK)

        except Exception as e:
            print("Entry creation failed: food")
            print(e.__class__.__name__)
            print(e)
            return HttpResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return HttpResponse(status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
def log_meal(request, client_id):
    """
    Log an existing meal (a meal exists if it is in the MealCache). If the meal does not exist, throws a 400 BAD REQUEST
    error (DialogFlow then tells the user they must create the meal before logging it).

    Expects a JSON in the following format:
    {
        "meal_name": "bacon and eggs"
    }
    """
    if request.method == 'POST':
        user, user_goals = get_or_create_user_and_goals(client_id)

        meal_data = JSONParser().parse(request)
        if "meal_name" in meal_data:
            meal_name = meal_data["meal_name"]
        else:
            return HttpResponse(status=status.HTTP_400_BAD_REQUEST)

        try:
            meal = get_meal(user, meal_name)
        except ObjectDoesNotExist:
            # Case if user hasn't created the meal they're trying to log
            return HttpResponse(status=status.HTTP_403_FORBIDDEN)

        curr_datetime = datetime.now()

        try:

            # Create meal entry
            Entry.objects.create(
                entry_id=md5_hash_string(str(user.user_id) + str(curr_datetime)),
                user_id=user,
                time_of_creation=curr_datetime,
                entry_name=meal_name,
                is_meal=True,
                kilocalories=meal.kilocalories,
                fat_grams=meal.fat_grams,
                protein_grams=meal.protein_grams,
                carb_grams=meal.carb_grams,
                water_ml=0
            )

            update_points_sprint_checkin(user, user_goals, curr_datetime)

            return HttpResponse(status=status.HTTP_200_OK)
        except Exception as e:
            print("Entry creation failed: meal")
            print(e.__class__.__name__)
            return HttpResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return HttpResponse(status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
def create_meal(request, client_id):
    """
    Create a meal and add it to the MealCache. A meal belongs to a specific user, and is associated with

    Example JSON structure:
    {
        "meal_name": "bacon and eggs",
        "food_details": {
            "food1": {
                "name": "bacon",
                "serving": 100,
            },
            "food2": {
                "name": "egg",
                "serving": 60,
            }
        }
    }
    """
    if request.method == 'POST':
        user, user_goals = get_or_create_user_and_goals(client_id)
        meal_data = JSONParser().parse(request)
        meal_name = meal_data["meal_name"]
        food_details = meal_data["food_details"]
        mb = utils.MealBuilder(meal_name, user)

        # Iterate through the food items in the JSON
        for food_title in utilconstants.FOOD_ENUM:
            if food_title in food_details:
                food = food_details[food_title]

                if "name" in food:
                    food_name = food["name"]
                else:
                    return HttpResponse(status=status.HTTP_400_BAD_REQUEST)

                if "serving" in food:
                    serving_size = food["serving"]
                else:
                    serving_size = user.serving_size

                mb.add_food(food_name, serving_size)

        try:
            mb.create_meal_record()
            return HttpResponse(status=status.HTTP_200_OK)

        except Exception as e:
            # Case if this meal already exists
            print(e.__class__.__name__)
            print(e)
            return HttpResponse(status=status.HTTP_403_FORBIDDEN)

    return HttpResponse(status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
def log_water(request, client_id):
    """
    Log some amount of water.
    Data about user's water intake is stored in DailyFood table.
    Receives a JSON that looks like this:
    {
        "water_ml": 250
    }
    """

    if request.method == 'POST':
        user, user_goals = get_or_create_user_and_goals(client_id)

        water_data = JSONParser().parse(request)
        if "water_ml" in water_data:
            water_ml = water_data["water_ml"]
        else:
            return HttpResponse(status=status.HTTP_400_BAD_REQUEST)

        curr_datetime = datetime.now()

        # Create water entry
        id_hash = md5_hash_string(user.user_id.__str__() + curr_datetime.__str__())
        print(id_hash)

        try:

            Entry.objects.create(
                entry_id=id_hash,
                user_id_id=user.user_id,
                time_of_creation=curr_datetime,
                entry_name="water",
                is_meal=False,
                kilocalories=0,
                fat_grams=0,
                protein_grams=0,
                carb_grams=0,
                water_ml=water_ml,
                is_water=True
            )

            update_points_sprint_checkin(user, user_goals, curr_datetime)

            return HttpResponse(status=status.HTTP_200_OK)

        except Exception as e:
            print("Entry creation failed: water")
            print(e.__class__.__name__)
            return HttpResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return HttpResponse(status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
def goals(request, client_id):
    """
    Get the user's current macro and water goals
    or
    Update the user's current macro and water goals
    """
    if request.method == 'GET':
        """
        Returns a JSON in the following format:
        {
            "water_ml": 2500,
            "carb_grams": 200,
            "protein_grams": 150,
            "fat_grams": 30
        }
        """
        user, user_goals = get_or_create_user_and_goals(client_id)
        goals_serializer = GoalsSerializer(user_goals)
        return JSONResponse(goals_serializer.data, status=status.HTTP_200_OK)

    if request.method == 'PUT':
        """
        Expects a JSON in the following format. Note that all the key-value pairs are optional,
        just that there has to be at least one parameter:
        {
            "water_ml": 2500,
            "carb_grams": 200,
            "protein_grams": 150,
            "fat_grams": 30
        }

        or even just

        {
            "water_ml": 3000
        }
        """
        user, user_goals = get_or_create_user_and_goals(client_id)
        raw_goal_data = JSONParser().parse(request)

        for goal_param in utilconstants.GOAL_PARAM_NAMES:
            if goal_param in raw_goal_data:
                param = raw_goal_data[goal_param]
                setattr(user_goals, goal_param, param)

        user_goals.save()
        return HttpResponse(status=status.HTTP_200_OK)

    return HttpResponse(status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
def points(request, client_id):
    """
    Handles GET points requests. Returns a JSON representation of the user's score in the following format:
    {
        "points": 347
    }
    """
    if request.method == 'GET':
        user_obj = get_or_create_user_and_goals(client_id)[0]
        user_serializer = UserSerializer(user_obj)
        # create new dict with just points data
        data = {"points": user_serializer.data["points"]}

        return JSONResponse(data, status=status.HTTP_200_OK)

    return HttpResponse(status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
def today_info(request, client_id):
    """
    Handles get requests and returns the quantities of macros and water that the user has consumed today.
    Returns a JSON in the following format:
    {
            "water_ml": 1200,
            "carb_grams": 87,
            "protein_grams": 22,
            "fat_grams": 13
    }
    """
    if request.method == 'GET':
        user = get_or_create_user_and_goals(client_id)[0]

        today_data = get_today_macros(user)

        return JSONResponse(today_data, status=status.HTTP_200_OK)

    return HttpResponse(status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
def food_info(request, client_id, food_name):
    """
    Handles GET FoodInfo requests. Returns a JSON representation of the FoodCache, using utils.py
    Returns a JSON in the following format:

    {
        "food_id": 3859057hjhdewasltw,
        "food_name": "banana"
        "kilocalories": 80
        "carb_grams": 12
        "protein_grams": 1
        "fat_grams": 0
    }

    """
    if request.method == 'GET':
        get_or_create_user_and_goals(client_id)

        try:
            food_cache_obj = get_food(food_name)
            food_cache_serializer = FoodCacheSerializer(food_cache_obj)
            return JSONResponse(food_cache_serializer.data, status=status.HTTP_200_OK)

        except RuntimeError:
            # This happens if the Nutritics API call in get_food() fails
            return HttpResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return HttpResponse(status=status.HTTP_400_BAD_REQUEST)
