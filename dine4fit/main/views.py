from django.shortcuts import render
from django.http import HttpResponse
from .models import Nutrient, DishCompositionNutrients, DishCompositionRequest

# Create your views here.
def chrome_devtools(request):
    """убирает ошибку GET /.well-known/appspecific/com.chrome.devtools.json HTTP/1.1 404 2710 при открытии кода страницы"""
    return HttpResponse(status=204)


def GetNutrients(request, dish_composition_request_id = 1):
    """Рендер страницы нутриентов + поиск"""

    nutrient_search_text = request.GET.get('nutrient_search_text', '')
    nutrient_types_amount = DishCompositionNutrients.objects.filter(dish_composition_request = dish_composition_request_id).count()
    
    data = {
        'nutrients': Nutrient.objects.filter(name__icontains=nutrient_search_text),
        'nutrient_search_text': nutrient_search_text,
        'nutrient_types_amount': nutrient_types_amount,
        'dish_composition_order_id': dish_composition_request_id,
    }
    return render(request, 'main/pages/nutrients_list.html', data)


def GetNutrientInfo(request, nutrient_id):
    """Рендер страницы нутриента"""
    nutrient = Nutrient.objects.filter(id=nutrient_id)[0]

    if nutrient:
        data = {'nutrient' : nutrient}
        return render(request, 'main/pages/nutrient_info.html', data)
    else:
        return HttpResponse(status=404)


def GetDishComposition(request, dish_composition_request_id):
    """Рендер страницы состава блюда"""

    data = {
        'dish_composition_order': DishCompositionRequest.objects.filter(id=dish_composition_request_id)[0],
        'dish_nutrients': DishCompositionNutrients.objects.filter(dish_composition_request = dish_composition_request_id).prefetch_related('nutrient')
    }

    return render(request, 'main/pages/dish_composition.html', data)