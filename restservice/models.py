from django.db import models
# from django.utils import timezone
import pytz


class Users(models.Model):
    TIMEZONES = tuple(zip(pytz.all_timezones, pytz.all_timezones))
    user_id = models.CharField(max_length=20, primary_key=True)
    # TODO: How do we pass in the name?? @assistant team
    name = models.CharField(max_length=150, unique=True)
    serving_size = models.IntegerField(default=100)
    streak = models.IntegerField()
    score = models.IntegerField()
    timezone = models.CharField(max_length=32, choices=TIMEZONES, default='EST')

    def __str__(self):
        return "{} has a score of {}, and has a streak of {}".format(self.name, self.score, self.streak)


class Goals(models.Model):
    goal_id = models.CharField(max_length=20, primary_key=True)
    user_id = models.ForeignKey("Users", on_delete=models.CASCADE)
    water_ml = models.IntegerField()
    protein_grams = models.IntegerField()
    fat_grams = models.IntegerField()
    carb_grams = models.IntegerField()
    kilocalories = models.IntegerField()

    def __str__(self):
        return "carbs: {}\nprotein: {}\nfat: {}\n kilocalories: {}".format(
            self.carb_grams,
            self.protein_grams,
            self.fat_grams,
            self.kilocalories
        )


class MealEntry(models.Model):
    meal_id = models.IntegerField(primary_key=True)
    user_id = models.ForeignKey("Users", on_delete=models.CASCADE)
    meal_name = models.CharField(max_length=100)
    time_of_creation = models.DateTimeField()
    # TODO: Added the following!
    kilocalories = models.IntegerField()
    fat_grams = models.IntegerField()
    carb_grams = models.IntegerField()
    protein_grams = models.IntegerField()

    def __str__(self):
        return "meal name: {}\ncarbs: {}\nprotein: {}\nfat: {}\n kilocalories: {}".format(
            self.meal_name,
            self.carb_grams,
            self.protein_grams,
            self.fat_grams,
            self.kilocalories
        )


class FoodEntry(models.Model):
    food_entry_id = models.IntegerField(primary_key=True)
    time_of_creation = models.DateTimeField()
    user_id = models.ForeignKey("Users", on_delete=models.CASCADE)
    meal_id = models.ForeignKey("MealEntry", on_delete=models.CASCADE, blank=True, NULL=True)   # Can be None, not all entries are meals
    nutritics_id = models.IntegerField(blank=True, NULL=True)
    food_name = models.CharField(max_length=100, blank=True, NULL=True)
    kilocalories = models.IntegerField()
    fat_grams = models.IntegerField()
    carb_grams = models.IntegerField()
    protein_grams = models.IntegerField()

    def __str__(self):
        return "food name: {}\ncarbs: {}\nprotein: {}\nfat: {}\n kilocalories: {}".format(
            self.food_name,
            self.carb_grams,
            self.protein_grams,
            self.fat_grams,
            self.kilocalories
        )


class DailyFood(models.Model):
    day_id = models.IntegerField(primary_key=True)
    time_of_creation = models.DateTimeField()
    user_id = models.ForeignKey("Users", on_delete=models.CASCADE)
    # One of the following two has to not be None!
    food_entry_id = models.ForeignKey("FoodEntry", on_delete=models.CASCADE, blank=True, NULL=True)
    meal_id = models.ForeignKey("MealEntry", on_delete=models.CASCADE, blank=True, NULL=True)

    def __str__(self):
        # TODO: Make this better?

        if self.food_entry_id is None:
            return "A meal was eaten"
        else:
            return "A food was eaten"
