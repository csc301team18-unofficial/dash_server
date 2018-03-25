from rest_framework import serializers
from restservice.models import *
import json


class FoodCacheSerializer(serializers.Serializer):
    food_hash = serializers.CharField(read_only=True, max_length=32)
    food_name = serializers.CharField(max_length=100)
    kilocalories = serializers.IntegerField()
    fat_grams = serializers.IntegerField()
    carb_grams = serializers.IntegerField()
    protein_grams = serializers.IntegerField()

    def create(self, validated_data):
        """
        :param validated_data: a dict where each key corresponds to a field in FoodCache
        """
        return FoodCache.objects.create(
                food_hash=validated_data["food_hash"],
                food_name=validated_data["food_name"],
                kilocalories=validated_data["kilocalories"],
                fat_grams=validated_data["fat_grams"],
                carb_grams=validated_data["carb_grams"],
                protein_grams=validated_data["protein_grams"]
        )

    def update(self, instance, validated_data):
        instance.food_name = validated_data.get('name', instance.name)
        instance.kilocalories = validated_data.get('kilocalories', instance.name)
        instance.fat_grams = validated_data.get('fat_grams', instance.name)
        instance.carb_grams = validated_data.get('carb_grams', instance.name)
        instance.protein_grames = validated_data.get('protein_grams', instance.name)
        instance.save()
        return instance


# class UserSerializer(serializers.Serializer):
#     user_id = serializers.CharField(max_length=20, read_only=True)
#     name = serializers.CharField(max_length=150, unique=True)
#     serving_size = serializers.IntegerField(default=100)
#     streak = serializers.IntegerField()
#     score = serializers.IntegerField()
#     timezone = serializers.CharField(max_length=32, choices=TIMEZONES, default='EST')
#
#     def create(self, validated_data):
#         """
#         :param validated_data: a dict where each key corresponds to a field in Users
#         """

class UserScoreSerializer(serializers.Serializer):
    def create(self, validated_data):
        """
        :param validated_data: an int corresponding to a User instance's score
        :return: JSON object containing the score
        """
        data = {"points":validated_data}
        json_data = json.dumps(data)

        return json_data

    def update(self, instance, validated_data):
        """
        :param instance: a User instance to update
        :param validated_data: an int corresponding to a User instance's new score
        :return: updated instance with the new code
        """
        instance.score = validated_data
        instance.save()
        return instance
