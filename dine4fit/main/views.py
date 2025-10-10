from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.db import models, connection
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.utils import timezone

from .models import Nutrient, DishCompositionNutrients, DishCompositionRequest, CustomUser
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt

from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from .serializers import DishCompositionNutrientSerializer, DishCompositionRequestFlatSerializer, DishCompositionRequestSerializer, NutrientSerializer, UserSerializer
from drf_yasg.utils import swagger_auto_schema

from .minio import add_pic, delete_pic

import re

# Create your views here.
def user():
    try:
        user1 = User.objects.get(id=1)
    except:
        user1 = User(id=1, first_name="Александр", last_name="Хомутинников", password='1234', username="user1")
        user1.save()
    return user1


class NutrientsAPIView(APIView):
    model_class = Nutrient
    serializer_class = NutrientSerializer

    def get(self, request, format=None):
        nutrient_search_text = request.GET.get('nutrient_search_text', '')  
        nutrients = self.model_class.objects.filter(name__icontains=nutrient_search_text, is_active = True)
        serializer = self.serializer_class(nutrients, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(request_body=NutrientSerializer)
    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class NutrientAPIView(APIView):
    model_class = Nutrient
    serializer_class = NutrientSerializer

    def get(self, request, pk, format=None):
        nutrient = get_object_or_404(self.model_class, pk=pk)
        serializer = self.serializer_class(nutrient)
        return Response(serializer.data)
    
    @swagger_auto_schema(request_body=NutrientSerializer)
    def post(self, request, pk, format=None):
        selected_nutrient = get_object_or_404(self.model_class, pk=pk)

        serializer = self.serializer_class(selected_nutrient) 

        try:
            dish_composition_draft = DishCompositionRequest.objects.get(client=user(), status=DishCompositionRequest.CompositionRequestStatus.DRAFT)

        except:
            dish_composition_draft = DishCompositionRequest.objects.create(client=user())

        DishCompositionNutrients.objects.get_or_create(
            dish_composition_request=dish_composition_draft,
            nutrient = selected_nutrient
        )

        return Response(serializer.data)

    @swagger_auto_schema(request_body=NutrientSerializer)
    def put(self, request, pk, format=None):
        nutrient = get_object_or_404(self.model_class, pk=pk)
        serializer = self.serializer_class(nutrient, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(request_body=NutrientSerializer)
    def delete(self, request, pk, format=None):
        nutrient = get_object_or_404(self.model_class, pk=pk)

        pic_result = delete_pic(nutrient)
        if 'error' in pic_result.data:
                return pic_result
        
        nutrient.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@swagger_auto_schema(method='post')
@api_view(['POST'])    
def post_img(request, pk, format=None):
    nutrient = get_object_or_404(Nutrient, pk=pk)
    if 'pic' in request.FILES:
        print('добавляем изображени')
        pic_result = add_pic(nutrient, request.FILES['pic'])
        if 'error' in pic_result.data:
            return pic_result

    return Response({'message': 'Изображение добавлено'}, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_dish_composition_draft(request):
    current_user = user()
    try:
        dish_composition_draft = DishCompositionRequest.objects.get(client=current_user, status=DishCompositionRequest.CompositionRequestStatus.DRAFT)
        nutrient_types_amount = DishCompositionNutrients.objects.filter(dish_composition_request = dish_composition_draft.pk).count()
        return Response({'dish_composition_draft': {'id': dish_composition_draft.id, 'nutrient_types_amount': nutrient_types_amount}}, status=status.HTTP_200_OK)
    except:
        return Response({'message': 'dish_composition_draft not created'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def get_dish_compositions(request):
    dish_composition_status = request.GET.get('dish_composition_status')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    dish_compositions = DishCompositionRequest.objects.exclude(
        status__in=['DR', 'DE']
    )

    if dish_composition_status:
        dish_compositions = dish_compositions.filter(status=dish_composition_status)
    if start_date and end_date:
        dish_compositions = dish_compositions.filter(creation_datetime__range=[start_date, end_date])

    serializer = DishCompositionRequestFlatSerializer(dish_compositions, many=True)

    return Response(serializer.data)


@swagger_auto_schema(method='put', request_body=DishCompositionRequestSerializer)
@api_view(['PUT'])
def put_dish_composition(request, pk):
    dish_composition = get_object_or_404(DishCompositionRequest, pk=pk)
    serializer = DishCompositionRequestSerializer(dish_composition, data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()

    return Response(serializer.validated_data)


@api_view(['DELETE'])
def delete_dish_composition(request, pk):
    dish_composition = get_object_or_404(DishCompositionRequest, pk=pk)

    if dish_composition.status == 'DE':
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    dish_composition.status = 'DE'
    dish_composition.formation_datetime = timezone.now()
    dish_composition.save()
    
    return Response({'message': 'Запрос на описание блюда успешно удален'}, status=status.HTTP_204_NO_CONTENT)


@swagger_auto_schema(method='put', request_body=DishCompositionRequestFlatSerializer)
@api_view(['PUT'])
def submit_dish_composition(request, pk):
    dish_composition = get_object_or_404(DishCompositionRequest, pk=pk)

    if dish_composition.status == 'DE':
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    if dish_composition.status != 'DR':
        return Response({'message': 'Запрос на описание блюда не в статусе черновика'}, status=status.HTTP_400_BAD_REQUEST)
    
    empty_fields = []
    fields = ['body_mass', 'dish_mass', 'dish']
    for field in fields:
        if not getattr(dish_composition, field, None):
            empty_fields.append(field)
    if empty_fields:
        empty_fields_str = ', '.join(empty_fields)
        return Response({'error': f'Заполните поля: {empty_fields_str}'}, status=status.HTTP_400_BAD_REQUEST)
    
    dish_composition.status = 'FO'
    dish_composition.formation_datetime = timezone.now()
    dish_composition.save()
    
    serializer = DishCompositionRequestFlatSerializer(dish_composition).data
    return Response({'message': 'Запрос на описание блюда сформирован', 'dish_composition': serializer}, status=status.HTTP_200_OK)


@swagger_auto_schema(method='put', request_body=DishCompositionRequestFlatSerializer)
@api_view(['PUT'])
def complete_dish_composition(request, pk):
    dish_composition = get_object_or_404(DishCompositionRequest, pk=pk)

    if dish_composition.status == 'DE':
        return Response({'error': 'Заявка удалена'}, status=status.HTTP_400_BAD_REQUEST)
    
    if dish_composition.status != 'FO':
        return Response({'error': 'Заявка должна быть в статусе Formed'}, status=status.HTTP_400_BAD_REQUEST)
    
    action = request.data.get('action')

    if not action or action not in ['complete', 'reject']:
        return Response({'error': 'Допустимые параметры: complete, reject'}, status=status.HTTP_400_BAD_REQUEST)

    if action == 'complete':
        dish_composition.status = 'CO'
        dish_composition.completion_date = timezone.now()
    elif action == 'reject':
        dish_composition.status = 'RE'
        dish_composition.completion_date = timezone.now()

    dish_composition.manager = user()
    dish_composition.date_completion = timezone.now()
    dish_composition.save()

    serializer = DishCompositionRequestFlatSerializer(dish_composition).data
    return Response({'message': f'Заявка успешно закрыта','dish_composition':serializer}, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_dish_composition(request, pk):
    dish_composition = get_object_or_404(DishCompositionRequest, pk=pk)
    serializer = DishCompositionRequestSerializer(dish_composition)

    return Response(serializer.data)


@api_view(['DELETE'])
def delete_dish_composition_nutrient(request, dish_composition_pk, nutrient_pk):
    dish_composition = get_object_or_404(dish_composition, pk=dish_composition_pk)

    if dish_composition.status == 'DE':
        return Response(status=status.HTTP_404_NOT_FOUND)

    nutrient = get_object_or_404(Nutrient, pk=nutrient_pk)
    dish_composition_nutrient = DishCompositionNutrients.objects.get(nutrient=nutrient, dish_composition=dish_composition)

    if dish_composition_nutrient:
        dish_composition_nutrient.delete()
        return Response({'message': 'Нутриент удален из запроса на описание'}, status=status.HTTP_204_NO_CONTENT)
    else:
        return Response({'error': 'Нутриент в заявке не найден'}, status=status.HTTP_404_NOT_FOUND)


@swagger_auto_schema(method='put', request_body=DishCompositionNutrientSerializer)
@api_view(['PUT'])
def put_dish_composition_nutrient(request, dish_composition_pk, nutrient_pk):
    dish_composition = get_object_or_404(DishCompositionRequest, pk=dish_composition_pk)
    nutrient = get_object_or_404(Nutrient, pk=nutrient_pk)

    dish_composition_nutrient = get_object_or_404(DishCompositionNutrients, nutrient=nutrient, dish_composition_request=dish_composition)
    serializer = DishCompositionNutrientSerializer(dish_composition_nutrient, data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()

    return Response(serializer.data)


# class UsersAPIView(APIView):
#     model_class = CustomUser
#     serializer_class = UserSerializer

#     def get(self, request, pk):
#         user = get_object_or_404(self.model_class, pk=pk)
#         serializer = self.serializer_class(user)
#         return Response(serializer.data)
    
#     @swagger_auto_schema(request_body=UserSerializer)
#     def put(self, request, pk):
#         user = get_object_or_404(User, id=pk)
#         serializer = self.serializer_class(user, data=request.data, partial=True)

#         serializer.is_valid(raise_exception=True)
#         serializer.save()

#         return Response(serializer.data)


# @csrf_exempt
# @swagger_auto_schema(method='post')
# @api_view(['POST'])
# def register_user(request):
#     data = request.data
#     username = data.get('username')
#     password = data.get('password')
#     email = data.get('email')

#     if User.objects.filter(username=username).exists():
#         return Response({'error': 'Пользователь с таким именем уже существует'}, status=status.HTTP_400_BAD_REQUEST)

#     if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
#         return Response({'error': 'Неверный формат email'}, status=status.HTTP_400_BAD_REQUEST)

#     user = User.objects.create_user(username=username, password=password, email=email)
#     return Response({'message': 'Пользователь успешно зарегистрирован'}, status=status.HTTP_201_CREATED)


# @csrf_exempt
# @swagger_auto_schema(method='post')
# @api_view(['POST'])
# def login_user(request):
#     data = request.data
#     username = data.get('username')
#     password = data.get('password')

#     user = authenticate(request, username=username, password=password)
#     if user is not None:
#         login(request, user)
#         return Response({'message': 'Пользователь успешно вошел в систему'}, status=status.HTTP_200_OK)
#     return Response({'error': 'Неверное имя пользователя или пароль'}, status=status.HTTP_401_UNAUTHORIZED)

# @csrf_exempt
# @swagger_auto_schema(method='post')
# @api_view(['POST'])
# def logout_user(request):
#     logout(request)
#     return Response({'message': 'Пользователь успешно вышел из системы'}, status=status.HTTP_200_OK)

class UserViewSet(viewsets.ModelViewSet):
    """Класс, описывающий методы работы с пользователями
    Осуществляет связь с таблицей пользователей в базе данных
    """
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    model_class = CustomUser

    def create(self, request):
        """
        Функция регистрации новых пользователей
        Если пользователя c указанным в request email ещё нет, в БД будет добавлен новый пользователь.
        """
        if self.model_class.objects.filter(email=request.data['email']).exists():
            return Response({'status': 'Exist'}, status=400)
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            print(serializer.data)
            self.model_class.objects.create_user(email=serializer.data['email'],
                                     password=serializer.data['password'],
                                     is_superuser=serializer.data['is_superuser'],
                                     is_staff=serializer.data['is_staff'])
            return Response({'status': 'Success'}, status=200)
        return Response({'status': 'Error', 'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)



    # @api_view(['Put'])
    # def put(self, request, pk, format=None):
    #     nutrient = get_object_or_404(self.model_class, pk=pk)
    #     serializer = self.serializer_class(nutrient, data=request.data, partial=True)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


"""
Рендер страниц в бразуере
"""


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