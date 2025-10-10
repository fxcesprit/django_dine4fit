from rest_framework import serializers
from collections import OrderedDict

from .models import DishCompositionNutrients, DishCompositionRequest, Nutrient#, AuthUser
from .models import CustomUser


class NutrientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Nutrient
        fields = ('name', 'daily_dose_min', 'daily_dose_max', 'short_desc', 'full_desc', 'img_url')

        def get_fields(self):
            new_fields = OrderedDict()
            for name, field in super().get_fields().items():
                field.required = False
                new_fields[name] = field
            return new_fields 


class DishCompositionNutrientSerializer(serializers.ModelSerializer):
    """Сериализатор для модели связи M2M"""
    nutrient = NutrientSerializer(read_only=True)
    
    class Meta:
        model = DishCompositionNutrients 
        fields = ('nutrient', 'quantity_in_dish', 'daily_dose_percentage')

        def get_fields(self):
            new_fields = OrderedDict()
            for name, field in super().get_fields().items():
                field.required = False
                new_fields[name] = field
            return new_fields   


class DishCompositionRequestSerializer(serializers.ModelSerializer):
    nutrients = DishCompositionNutrientSerializer(
        source='dishcompositionnutrients_set',
        many=True,
        read_only=True
    )
    class Meta:
        model = DishCompositionRequest
        fields = ('status', 'creation_datetime', 'formation_datetime', 'completion_datetime', 'client', 'manager', 'body_mass', 'dish_mass', 'dish', 'nutrients')
        read_only_fields = ('status', 'creation_datetime', 'formation_datetime', 'completion_datetime', 'client', 'manager')

        def get_fields(self):
            new_fields = OrderedDict()
            for name, field in super().get_fields().items():
                field.required = False
                new_fields[name] = field
            return new_fields 
        

class DishCompositionRequestFlatSerializer(serializers.ModelSerializer):
    client = serializers.CharField(source='client.username', read_only=True)
    manager = serializers.CharField(source='manager.username', read_only=True)
    class Meta:
        model = DishCompositionRequest
        fields = ('status', 'creation_datetime', 'formation_datetime', 'completion_datetime', 'client', 'manager', 'body_mass', 'dish_mass', 'dish')
        read_only_fields = ('status', 'creation_datetime', 'formation_datetime', 'completion_datetime', 'client', 'manager')

        def get_fields(self):
            new_fields = OrderedDict()
            for name, field in super().get_fields().items():
                field.required = False
                new_fields[name] = field
            return new_fields 
        

# class AuthUserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = AuthUser
#         fields = ('username', 'email', 'date_joined')

#         def get_fields(self):
#             new_fields = OrderedDict()
#             for name, field in super().get_fields().items():
#                 field.required = False
#                 new_fields[name] = field
#             return new_fields 

class UserSerializer(serializers.ModelSerializer):
    is_staff = serializers.BooleanField(default=False, required=False)
    is_superuser = serializers.BooleanField(default=False, required=False)
    class Meta:
        model = CustomUser
        fields = ['email', 'password', 'is_staff', 'is_superuser']