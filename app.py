from flask import Flask
from flask_restful import Api, Resource, reqparse
from pymongo import MongoClient
import os
import shutil
import requests

app = Flask(__name__)
api = Api(app)

client = MongoClient()
db = client.datasets_db

# Bing API
subscription_key = 'b6f1f528a8d7468fa2baa1e3e29fbfba'
search_url = 'https://api.cognitive.microsoft.com/bing/v7.0/images/search'
headers = {'Ocp-Apim-Subscription-Key': subscription_key}

TRAIN_TEST_RATIO = 0.8  # Соотношение train и test выборок


class Dataset(Resource):
    # Поиск датасета по названию в Bing
    # Загрузка изображений и сохранение информации в MongoDB
    def put(self):
        # Парсим запрос
        parser = reqparse.RequestParser()
        parser.add_argument('dataset_name', required=True)
        parser.add_argument('dataset_size', required=True, type=int)
        params = parser.parse_args()
        dataset_name = params['dataset_name']
        dataset_size = params['dataset_size']

        # Если уже есть папка датасета
        if os.path.exists(dataset_name):
            shutil.rmtree(dataset_name)
        # Создаем папку датасета
        while True:
            try:
                os.mkdir(dataset_name)
                break
            except PermissionError:  # Win 10 permission error ¯\_(ツ)_/¯
                pass

        # Если уже есть коллекция в БД - удаляем
        if dataset_name in db.list_collection_names():
            db[dataset_name].drop()

        completed = 0  # Количество успешно полученных изображений
        offset = 0  # Пропустить первых n результатов

        # Пока не будет получено необходимое количество изображений
        while completed < dataset_size:
            # Ищем в Bing
            params = {'q': dataset_name, 'count': dataset_size - completed, 'offset': offset}
            response = requests.get(search_url, headers=headers, params=params).json()
            search_results = response['value']

            # Если не нашлось необходимое количество изображений по запросу
            if len(search_results) < dataset_size - completed:
                if os.path.exists(dataset_name):
                    shutil.rmtree(dataset_name)  # Удаляем папку датасета
                if dataset_name in db.list_collection_names():
                    db[dataset_name].drop()  # Удаляем коллекцию датасета в БД
                return {'error': 'Can not find requested number of images!'}, 400

            offset = response['nextOffset']  # Обновляем offset для следующего поиска

            # Проходим по результатам поиска
            for img in search_results:
                # Пытаемся получить изображение
                try:
                    response = requests.get(img['contentUrl'], stream=True, timeout=1)
                    response.raise_for_status()  # raise HTTPError
                    path = dataset_name + '/' + str(completed) + '.' + img['encodingFormat']
                    # Загружаем изображение
                    with open(path, 'wb') as file:
                        response.raw.decode_content = True
                        shutil.copyfileobj(response.raw, file)
                    # Исключение если файл пустой
                    if os.path.getsize(path) == 0:
                        raise Exception('File is empty!')
                    # Сохраняем в БД
                    document = {'url': img['contentUrl'],
                                'path': path}
                    db[dataset_name].insert_one(document)
                    # Если не было исключений
                    completed += 1
                except Exception:  # Если были - переходим к следующему результату поиска
                    pass

        # Когда получено необходимое количество изображений
        return {'info': 'Dataset collected'}, 201

    # Просмотр сохраненного датасета
    # Возвращает train и test выборки (соотношение 80:20)
    def get(self):
        # Парсим запрос
        parser = reqparse.RequestParser()
        parser.add_argument('dataset_name', required=True)
        params = parser.parse_args()

        dataset_name = params['dataset_name']

        # Если такого датасета нет в БД
        if dataset_name not in db.list_collection_names():
            return {'error': 'Dataset not found!'}, 404

        dataset_size = db[dataset_name].count_documents({})
        train_size = round(dataset_size * TRAIN_TEST_RATIO)

        # Получаем train и test выборки без поля _id
        train = list(db[dataset_name].find({}, projection={'_id': False}, limit=train_size))
        test = list(db[dataset_name].find({}, projection={'_id': False}, skip=train_size))

        # Возвращаем train и test
        return {'train': train, 'test': test}, 200

    # Удаление изображения из датасета по URL
    def delete(self):
        # Парсим запрос
        parser = reqparse.RequestParser()
        parser.add_argument('dataset_name', required=True)
        parser.add_argument('url', required=True)
        params = parser.parse_args()

        dataset_name = params['dataset_name']
        url = params['url']

        # Если есть такой датасет
        if dataset_name in db.list_collection_names():
            # Если есть изображение с таким URL - удаляем
            if db[dataset_name].find_one({'url': url}):
                path = db[dataset_name].find_one({'url': url})['path']
                os.remove(path)
                db[dataset_name].delete_one({'url': url})
                return {'info': 'Image deleted'}, 200
            else:
                return {'error': 'URL not found!'}, 404
        else:
            return {'error': 'Dataset not found!'}, 404


api.add_resource(Dataset, '/datasets/api')

if __name__ == '__main__':
    app.run(debug=False)
