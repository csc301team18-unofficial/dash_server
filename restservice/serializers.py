from rest_framework import serializers
from restservice.models import *


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
        return FoodCache.objects.create(dict(
                food_hash=validated_data["food_hash"],
                food_name=validated_data["food_name"],
                kilocalories=validated_data["kilocalories"],
                fat_grams=validated_data["fat_grams"],
                carb_grams=validated_data["carb_grams"],
                protein_grams=validated_data["protein_grams"]
            )
        )

    def update(self, instance, validated_data):
        instance.food_name = validated_data.get('name', instance.name)
        instance.kilocalories = validated_data.get('kilocalories', instance.name)
        instance.fat_grams = validated_data.get('fat_grams', instance.name)
        instance.carb_grams = validated_data.get('carb_grams', instance.name)
        instance.protein_grames = validated_data.get('protein_grams', instance.name)
        instance.save()
        return instance
