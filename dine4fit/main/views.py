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
        'img': '',
    },
    {
        'id': 2,
        'name': 'Жиры',
        'daily_dose_min': 0.8,
        'daily_dose_max': 1.2,
        'short_desc': 'Запас энергии, защита органов и усвоение витаминов',
        'full_desc': '',
        'img': '',
    },
    {
        'id': 3,
        'name': 'Углеводы',
        'daily_dose_min': 3,
        'daily_dose_max': 5,
        'short_desc': 'Основной источник энергии',
        'full_desc': '',
        'img': '',
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


# Create your views here.
def chrome_devtools(request):
    """убирает ошибку GET /.well-known/appspecific/com.chrome.devtools.json HTTP/1.1 404 2710 при открытии кода страницы"""
    return HttpResponse(status=204)


def GetNutrients(request):
    """Рендер страницы нутриентов + поиск"""

    search_text = ''

    if request.method == 'POST':
        search_text = request.POST.get('search_text', '').strip()
    
    if search_text:
        filtered_nutrients = [
            nutrient for nutrient in nutrients
            if search_text.lower() in nutrient['name'].lower()
        ]
    else:
        filtered_nutrients = nutrients
    
    data = {
        'nutrients': filtered_nutrients,
        'search_text': search_text 
    }
    return render(request, 'main/nutrients_list.html', data)


def GetNutrientInfo(request, nutrient_id):

    found_nutrient = dict()

    for nutrient in nutrients:
        if nutrient['id'] == nutrient_id:
            found_nutrient = nutrient

    if found_nutrient:
        data = {'nutrient' : found_nutrient}
        return render(request, 'main/nutrient_info.html', data)
    else:
        return HttpResponse(status=404)


def GetDishComposition(request):
    return render(request, 'main/dish_composition.html')