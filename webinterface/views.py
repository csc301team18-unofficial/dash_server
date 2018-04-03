from django.shortcuts import render

from django.http import HttpResponse
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from restservice.models import *

from utility.utils import *


def insights(request, client_name):

    try:
        # user_data = get_relevant_user_data(client_name)
        if client_name == 'democlient':
            data = get_dummy_data_for_html("AngryAnnoyedAardvark")
        else:
            data = get_relevant_user_data(client_name)

        return render(request, "insights/insights.html", data)

    except ObjectDoesNotExist:
        # TODO: The user doesn't have an account, so render an error page telling them to use the app at least once
        print("user account for {} does not exist".format(client_name))
        return HttpResponse(status=status.HTTP_404_NOT_FOUND)


###################
# TESTING ONLY
###################

def get_dummy_data_for_html(username):
    """
    Return dummy dictionary to display on HTML.

    :param userid: User id
    :return: dict
    """
    user_dict = {
        'username': username,
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
        'curr_user_water': 2000,
        'user_water_goal': 3780,
        'user_water_percentage': 53,
        'curr_user_cals': 1260,
        'user_cals_goal': 2050,
        'user_cals_percentage': 61,
        'breakfast_foods': ["Toast", "Eggs", "Banana"],
        'lunch_foods': ["Pizza", "Apple"],
        'dinner_foods': ["Pasta", "Broccoli"]
    }
    return user_dict
