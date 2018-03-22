from django.db import models


class Users(models.Model):
    user_id = models.CharField(max_length=20, primary_key=True)
    name = models.CharField(max_length=150)
    serving_size = models.IntegerField()
    streak = models.IntegerField()
    score = models.IntegerField()


class Goals(models.Model):
    goal_id = models.CharField(max_length=20, primary_key=True)
    user_id = models.ForeignKey("Users", on_delete=models.CASCADE)
    water_ml = models.IntegerField()
    protein_grams = models.IntegerField()
    fat_grams = models.IntegerField()
    carb_grams = models.IntegerField()
    calories = models.IntegerField()


class MealEntry(models.Model):
    meal_id = models.IntegerField(primary_key=True)
    user_id = models.ForeignKey("Users", on_delete=models.CASCADE)
    meal_name = models.CharField(max_length=100)
    time_of_creation = models.DateTimeField()
    # TODO: Added these!
    kilocalories = models.IntegerField()
    fat_grams = models.IntegerField()
    carb_grams = models.IntegerField()
    protein_grams = models.IntegerField()


class FoodEntry(models.Model):
    food_entry_id = models.IntegerField(primary_key=True)
    time_of_creation = models.DateTimeField()
    user_id = models.ForeignKey("Users", on_delete=models.CASCADE)
    meal_id = models.ForeignKey("Meal", on_delete=models.CASCADE)   # Can be None, not all entries are meals
    nutritics_id = models.IntegerField()
    food_name = models.CharField(max_length=100)
    # TODO: Do we need this?
    # serving_size = models.IntegerField()
    kilocalories = models.IntegerField()
    fat_grams = models.IntegerField()
    carb_grams = models.IntegerField()
    protein_grams = models.IntegerField()


class DailyFood(models.Model):
    day_id = models.IntegerField(primary_key=True)
    time_of_creation = models.DateTimeField()
    user_id = models.ForeignKey("Users", on_delete=models.CASCADE)
    # One of these two has to not be None!
    food_entry_id = models.ForeignKey("FoodEntry", on_delete=models.CASCADE)
    meal_id = models.ForeignKey("MealEntry", on_delete=models.CASCADE)
