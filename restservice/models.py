from django.db import models


class Users(models.Model):
    user_id = models.CharField(max_length=100, primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    serving_size = models.IntegerField(default=100)
    sprint = models.IntegerField()
    points = models.IntegerField()
    last_checkin = models.DateTimeField()   # Used to calculate the streak, updated with every logging request

    def __str__(self):
        return self.user_id


class Goals(models.Model):
    goal_id = models.CharField(max_length=32, primary_key=True)
    user_id = models.ForeignKey("Users", on_delete=models.CASCADE)
    water_ml = models.IntegerField()
    protein_grams = models.IntegerField()
    fat_grams = models.IntegerField()
    carb_grams = models.IntegerField()
    kilocalories = models.IntegerField()

    def __str__(self):
        return self.goal_id


class Entry(models.Model):
    """
    Each entry is one thing that user user_id ate, with the nutrition data
    scaled to the appropriate amounts, given the user's portion size.
    """
    # EntryID is generated by md5 hashing the concatenation of user_id and time_of_creation
    entry_id = models.CharField(max_length=32, primary_key=True)
    user_id = models.ForeignKey("Users", on_delete=models.CASCADE)
    time_of_creation = models.DateTimeField()
    entry_name = models.CharField(max_length=100, blank=True, null=True)
    is_meal = models.BooleanField(default=False)
    kilocalories = models.IntegerField()
    fat_grams = models.IntegerField()
    carb_grams = models.IntegerField()
    protein_grams = models.IntegerField()
    water_ml = models.IntegerField(null=True)
    is_water = models.BooleanField(default=False)

    def __str__(self):
        return self.entry_id


class MealCache(models.Model):
    """
    Nutrition data for meals that the user creates.

    """
    # ID is generated from the MD5 hash of the meal's name concatenated with the user_id
    meal_id = models.CharField(primary_key=True, max_length=32)
    meal_name = models.CharField(max_length=100)
    user_id = models.ForeignKey("Users", on_delete=models.CASCADE)
    kilocalories = models.IntegerField()
    fat_grams = models.IntegerField()
    carb_grams = models.IntegerField()
    protein_grams = models.IntegerField()

    def __str__(self):
        return self.meal_id


class FoodCache(models.Model):

    # Hash is generated by calling the md5_hash_string() function on the food's name
    food_id = models.CharField(primary_key=True, max_length=32)
    food_name = models.CharField(max_length=100)
    # All these measurements are ALWAYS per 100 grams of food
    kilocalories = models.IntegerField()
    fat_grams = models.IntegerField()
    carb_grams = models.IntegerField()
    protein_grams = models.IntegerField()

    def __str__(self):
        return self.food_id
