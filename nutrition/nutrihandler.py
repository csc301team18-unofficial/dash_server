import requests
from nutrition import nutritics_constants as nc

class Meal:


    def __init__(self, name):
        self.foods = []

class Food:
    """
    Container / utility class that represents a food that the user is trying to log.
    """

    def __init__(self, food_id, food_name, k_cal, carb, protein, fat):
        self.id = food_id
        self.name = food_name
        self.k_cal = k_cal
        self.carb = carb
        self.protein = protein
        self.fat = fat




class NutriHandler:

    def __init__(self, client_id):
        self.client_id = client_id
        self.serving_size = self.getServingSize(client_id)
        print("created a client nutrition handler")

    def food_request(self, food_name):
        r =requests.get(self.build_req_string(food_name), auth=(nc.NUTRITICS_USER, nc.NUTRITICS_PSWD))

    def build_food_req_string(self, food_name):
        theurl = 'https://www.nutritics.com/api/v1.1/LIST/&food=burger&attr=energyKcal,carbohydrate,protein,fat

    def get_serving_size(self, client_id):
