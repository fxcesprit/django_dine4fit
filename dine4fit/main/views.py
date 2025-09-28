from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.db import models, connection
from django.contrib.auth.decorators import login_required

from .models import Nutrient, DishCompositionNutrients, DishCompositionRequest
from django.contrib.auth.models import User

# Create your views here.
def chrome_devtools(request):
    """убирает ошибку GET /.well-known/appspecific/com.chrome.devtools.json HTTP/1.1 404 2710 при открытии кода страницы"""
    return HttpResponse(status=204)


def GetNutrients(request):
    """Рендер страницы нутриентов + поиск"""

    try:
        dish_composition_draft = DishCompositionRequest.objects.get(client=request.user, status=DishCompositionRequest.CompositionRequestStatus.DRAFT)
        nutrient_types_amount = DishCompositionNutrients.objects.filter(dish_composition_request = dish_composition_draft.pk).count()
        data = {
            'dish_composition_order_id': dish_composition_draft.pk,
            'nutrient_types_amount': nutrient_types_amount,
            }

        
    except:
        data = {}

    nutrient_search_text = request.GET.get('nutrient_search_text', '')
    
    data = data | {
        'nutrients': Nutrient.objects.filter(name__icontains=nutrient_search_text, is_active = True),
        'nutrient_search_text': nutrient_search_text,
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


@login_required
def GetDishComposition(request, dish_composition_request_id):
    """Рендер страницы состава блюда"""

    dish_comp_req = get_object_or_404(DishCompositionRequest, id=dish_composition_request_id)
    
    if dish_comp_req.status == DishCompositionRequest.CompositionRequestStatus.DELETED:
        return HttpResponse(status=404)

    data = {
        'dish_composition_order': dish_comp_req,
        'dish_nutrients': DishCompositionNutrients.objects.filter(dish_composition_request = dish_composition_request_id)
    }

    return render(request, 'main/pages/dish_composition.html', data)


@login_required
def AddDishCompositionNutrient(request, nutrient_id):

    try:
        dish_composition_draft = DishCompositionRequest.objects.get(client=request.user, status=DishCompositionRequest.CompositionRequestStatus.DRAFT)

    except:
        dish_composition_draft = DishCompositionRequest.objects.create(client=request.user)
        
    selected_nutrient = get_object_or_404(Nutrient, id=nutrient_id)

    DishCompositionNutrients.objects.get_or_create(
        dish_composition_request=dish_composition_draft,
        nutrient = selected_nutrient
        )

    return redirect('nutrients_list_url')


@login_required
def DeleteDishComposition(request, dish_composition_request_id):
    
    dish_comp_req = get_object_or_404(DishCompositionRequest, id=dish_composition_request_id)
    
    if dish_comp_req.status == DishCompositionRequest.CompositionRequestStatus.DELETED:
        return HttpResponse(status=404)
    

    with connection.cursor() as cursor:
        cursor.execute("""
            UPDATE main_dishcompositionrequest
            SET status = 'DE'
            WHERE id = %s
            """, [dish_composition_request_id])
        return redirect('nutrients_list_url')