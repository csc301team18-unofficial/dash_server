from django.shortcuts import render

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from restservice.models import *

from utility.utils import *


def insights(request, client_name):

    print("WE'RE IN INSIGHTS BOI")

    try:
        user_data = get_relevant_user_data(client_name)
        return render(request, "templates/insights/insights.html",
                      get_dummy_data_for_html("blah"))

    except ObjectDoesNotExist:
        # TODO: The user doesn't have an account, so render an error page telling them to use the app at least once
        # TODO: or something like that
        print("user account for {} does not exist".format(client_name))

    pass


def get_relevant_user_data(client_name):
    """
    TODO:
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

    user_goals = Goals.objects.get(user_id=user.user_id)
    user_data = dict()

    # Add goals and other stats to user
    user_data["points"] = user.score
    user_data["sprint"] = user.streak
    user_data["carb_goal"] = user_goals.carb_grams
    user_data["fat_goal"] = user_goals.fat_grams
    user_data["protein_goal"] = user_goals.protein_grams
    user_data["kcal_goal"] = user_goals.kilocalories
    user_data["water_goal"] = user_goals.water_ml

    # TODO: Add the user's stats for TODAY, i.e how much carbs / fats / proteins / water they've consumed so far

    return user_data


def get_dummy_data_for_html(userid):
    """
    Return dummy dictionary to display on HTML.

    :param userid: User id
    :return: dict
    """
    user_dict = {
        'streak': 29,
        'user_score': 101,
        'curr_user_carbs': 120,
        'user_carbs_goal': 200,
        'user_carbs_percentage': 60,
        'curr_user_protein': 150,
        'user_protein_goal': 200,
        'user_protein_percentage': 75,
        'curr_user_fat': 20,
        'user_fat_goal': 50,
        'user_fat_percentage': 40,
        'curr_user_cals': 1260,
        'user_cals_goal': 2050,
        'user_cals_percentage': 61,
        'breakfast_foods': ["Toast", "Eggs", "Banana"],
        'lunch_foods': ["Pizza", "Apple"],
        'dinner_foods': ["Pasta", "Broccoli"]
    }
    return user_dict
