# PUT — Сбор датасета
## Запрос
```
PUT /datasets/api HTTP/1.1
Content-Type: application/json
Host: 127.0.0.1:5000

{
    "dataset_name": "cat",
    "dataset_size": 50
}
```

### Параметры
* dataset_name — название датасета для поиска
* dataset_size — размер датасета

## Пример ответа
```
201 CREATED

{
  "info": "Dataset collected"
}
```

# GET — Просмотр сохранённого датасета
## Запрос
```
GET /datasets/api HTTP/1.1
Content-Type: application/json
Host: 127.0.0.1:5000
 
{
    "dataset_name": "dog"
}
```

### Параметры
* dataset_name — название датасета

## Пример ответа
```
200 OK

{
  "train": [
    {
      "url": "https://www.katrinawilsonphotography.co.uk/wp-content/uploads/2015/01/Katrina-Wilson-Dog-Photographer-Golden-Retriever_.jpg",
      "path": "dog/0.jpeg"
    },
    
    ...
    
    {
      "url": "https://s-media-cache-ak0.pinimg.com/736x/44/e8/58/44e858408b8187ac5c8531de884b88e0.jpg",
      "path": "dog/39.jpeg"
    }
  ],
  "test": [
    {
      "url": "https://www.bluecross.org.uk/sites/default/files/assets/images/Puppy%20hiding%20behind%20bed.jpg",
      "path": "dog/40.jpeg"
    },
    
    ...
    
    {
      "url": "https://www.katrinawilsonphotography.co.uk/wp-content/uploads/2015/01/Katrina-Wilson-Dog-Photographer-Bedfordshire-UK-11.jpg",
      "path": "dog/49.jpeg"
    }
  ]
}
```

# DELETE — Удаление изображения по URL
## Запрос
```
DELETE /datasets/api HTTP/1.1
Content-Type: application/json
Host: 127.0.0.1:5000
 
{
    "dataset_name": "cat",
    "url": "http://pawspetphotography.co.uk/files/9414/5342/1556/PPP222.jpg"
}
```

### Параметры
* dataset_name — название датасета
* url — URL изображения для удаления

## Пример ответа
```
200 OK
 
{
  "info": "Image deleted"
}
```