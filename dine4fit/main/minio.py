from django.conf import settings
from minio import Minio
from django.core.files.uploadedfile import InMemoryUploadedFile
from rest_framework.response import *

def process_file_upload(file_object: InMemoryUploadedFile, client, image_name):
    try:
        client.put_object(f'{settings.AWS_STORAGE_BUCKET_NAME}', image_name, file_object, file_object.size)
        return f"http://localhost:9000/{settings.AWS_STORAGE_BUCKET_NAME}/{image_name}"
    except Exception as e:
        return {"error": str(e)}
    

def process_file_delete(client, image_name):
    try:
        client.remove_object(settings.AWS_STORAGE_BUCKET_NAME, image_name)
        return f"http://localhost:9000/{settings.AWS_STORAGE_BUCKET_NAME}/{image_name}"
    except Exception as e:
        return {"error": str(e)}


def delete_pic(nutrient):
    client = Minio(           
            endpoint=settings.AWS_S3_ENDPOINT_URL,
           access_key=settings.AWS_ACCESS_KEY_ID,
           secret_key=settings.AWS_SECRET_ACCESS_KEY,
           secure=settings.MINIO_USE_SSL
    )
    i = nutrient.id

    if not nutrient.img_url:
        return Response({"message": "no img_url"})
    img_obj_name = f'Nutrient{i}'

    result = process_file_delete(client, img_obj_name)

    if 'error' in result:
        return Response(result)

    return Response({"message": "success"})


def add_pic(nutrient, pic):
    client = Minio(           
            endpoint=settings.AWS_S3_ENDPOINT_URL,
           access_key=settings.AWS_ACCESS_KEY_ID,
           secret_key=settings.AWS_SECRET_ACCESS_KEY,
           secure=settings.MINIO_USE_SSL
    )
    i = nutrient.id
    img_obj_name = f'Nutrient{i}'

    if not pic:
        return Response({"error": "Нет файла для изображения логотипа."})
    
    # if nutrient.img_url:
    #     process_file_delete(client, img_obj_name)

    result = process_file_upload(pic, client, img_obj_name)

    if 'error' in result:
        return Response(result)

    nutrient.img_url = result
    nutrient.save()

    return Response({"message": "success"})