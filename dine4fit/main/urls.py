"""
URL configuration for dine4fit project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from . import views

urlpatterns = [
    #GET
    path('', views.GetNutrients, name='nutrients_list_url'),
    path('nutrient/<int:nutrient_id>', views.GetNutrientInfo, name='nutrient_info_url'),
    path('dish_composition/<int:dish_composition_request_id>', views.GetDishComposition, name='dish_composition_url'),

    #POST
    path('nutrient/add_dish_composition_nutrient/<int:nutrient_id>', views.AddDishCompositionNutrient, name='add_dish_composition_nutrient_url'),
    path('dish_composition/<int:dish_composition_request_id>/delete', views.DeleteDishComposition, name='delete_dish_composition_url'),
        
    #API
    path('api/v1/nutrients', views.NutrientsAPIView.as_view()),
    path('api/v1/nutrients/<int:pk>', views.NutrientAPIView.as_view()),
    path('api/v1/nutrients/<int:pk>/img', views.post_img),

    path('api/v1/dish_compositions/draft', views.get_dish_composition_draft),
    path('api/v1/dish_compositions', views.get_dish_compositions),
    path('api/v1/dish_compositions/<int:pk>', views.get_dish_composition),
    path('api/v1/dish_compositions/<int:pk>/put', views.put_dish_composition),
    path('api/v1/dish_compositions/<int:pk>/submit', views.submit_dish_composition),
    path('api/v1/dish_compositions/<int:pk>/complete', views.complete_dish_composition),
    path('api/v1/dish_compositions/<int:pk>/delete', views.delete_dish_composition),

    path('api/v1/dish_compositions/<int:dish_compositions_pk>/nutrient/<int:nutrient_pk>/delete', views.delete_dish_composition_nutrient),
    path('api/v1/dish_compositions/<int:dish_compositions_pk>/nutrient/<int:nutrient_pk>/put', views.put_dish_composition_nutrient),

    path('api/v1/users/<int:pk>', views.UsersAPIView.as_view()),
    path('api/v1/users/register', views.register_user),
    path('api/v1/users/login', views.login_user),
    path('api/v1/users/logout', views.logout_user),
    
    #Other
    path('.well-known/appspecific/com.chrome.devtools.json', views.chrome_devtools), # убирает ошибку GET /.well-known/appspecific/com.chrome.devtools.json HTTP/1.1 404 2710 при открытии кода страницы
]
