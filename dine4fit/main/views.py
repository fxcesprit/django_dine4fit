from django.shortcuts import render
from django.http import HttpResponse


nutrients = [
    {
        'id': 1,
        'name': 'Белки',
        'daily_dose_min': 1.2,
        'daily_dose_max': 1.7,
        'short_desc': 'Строительный материал для мышц и клеток',
        'full_desc': '''Белки — это главный строительный материал организма. Они расщепляются на аминокислоты, которые используются для создания и восстановления мышечной ткани, органов, кожи, волос и ногтей. Также белки входят в состав ферментов, гормонов и антител, играя критическую роль практически во всех биологических процессах — от переваривания пищи до защиты от инфекций. Достаточное потребление белка необходимо для поддержания силы, восстановления после тренировок и долгосрочного здоровья.

Основные источники белка: мясо, птица, рыба, молоко, орехи, бобовые, зерновые, овощи, фрукты, ягоды и грибы.''',
        'img': 'http://127.0.0.1:9000/bucket/%D0%B1%D0%B5%D0%BB%D0%BE%D0%BA.jpg',
    },
    {
        'id': 2,
        'name': 'Жиры',
        'daily_dose_min': 0.8,
        'daily_dose_max': 1.2,
        'short_desc': 'Запас энергии, защита органов и усвоение витаминов',
        'full_desc': '',
        'img': 'http://127.0.0.1:9000/bucket/Healthy-fats.webp',
    },
    {
        'id': 3,
        'name': 'Углеводы',
        'daily_dose_min': 3,
        'daily_dose_max': 5,
        'short_desc': 'Основной источник энергии',
        'full_desc': '',
        'img': 'http://127.0.0.1:9000/bucket/shutterstock_731206732.webp',
    },
    {
        'id': 4,
        'name': 'Магний',
        'daily_dose_min': 1.2,
        'daily_dose_max': 1.7,
        'short_desc': 'Минерал спокойствия и энергии',
        'full_desc': '',
        'img': '',
    },
    {
        'id': 5,
        'name': 'Витамин C',
        'daily_dose_min': 0.8,
        'daily_dose_max': 1.2,
        'short_desc': 'Главный антиоксидант и защитник',
        'full_desc': '',    
        'img': '',
    },
]

dish_nutrients = [
    {
        'dish_composition_order_id': 1,
        'nutrient_id': 1,
        'amount_in_dish': 10,
        'daily_dose_percentage': 2,
    },

    {
        'dish_composition_order_id': 1,
        'nutrient_id': 2,
        'amount_in_dish': 12,
        'daily_dose_percentage': 3,
    }
]

dish_composition_orders = [
    {
        'id': 1,
        'dish': 'яйцо',
        'body_mass': 80,
        'dish_mass': 100,
    },
]


# Create your views here.
def chrome_devtools(request):
    """убирает ошибку GET /.well-known/appspecific/com.chrome.devtools.json HTTP/1.1 404 2710 при открытии кода страницы"""
    return HttpResponse(status=204)


def GetNutrients(request, dish_composition_order_id = 1):
    """Рендер страницы нутриентов + поиск"""

    nutrient_search_text = request.GET.get('nutrient_search_text', '')
    nutrient_types_amount = len([rec for rec in dish_nutrients if rec['dish_composition_order_id'] == dish_composition_order_id])
    
    if nutrient_search_text:
        filtered_nutrients = [
            nutrient for nutrient in nutrients
            if nutrient_search_text.lower() in nutrient['name'].lower()
        ]
    else:
        filtered_nutrients = nutrients
    
    data = {
        'nutrients': filtered_nutrients,
        'nutrient_search_text': nutrient_search_text,
        'nutrient_types_amount': nutrient_types_amount,
        'dish_composition_order_id': dish_composition_order_id,
    }
    return render(request, 'main/pages/nutrients_list.html', data)


def GetNutrientInfo(request, nutrient_id):
    """Рендер страницы нутриента"""
    nutrient = next((n for n in nutrients if n['id'] == nutrient_id), None)

    if nutrient:
        data = {'nutrient' : nutrient}
        return render(request, 'main/pages/nutrient_info.html', data)
    else:
        return HttpResponse(status=404)


def GetDishComposition(request, dish_composition_order_id):
    """Рендер страницы состава блюда"""
    # Селект заказа по айди
    dish_composition_order = next((o for o in dish_composition_orders if o['id'] == dish_composition_order_id), None)
    # Селект и join нутриентов в заказе
    dish_nutrients_local = [
        rec | next((n for n in nutrients if n['id'] == rec['nutrient_id']), None) # join нутриента в блюде и информации о нутриенте
        for rec in dish_nutrients 
        if rec['dish_composition_order_id'] == dish_composition_order_id
    ]

    data = {
        'dish_composition_order': dish_composition_order,
        'dish_nutrients': dish_nutrients_local,
    }

    return render(request, 'main/pages/dish_composition.html', data)