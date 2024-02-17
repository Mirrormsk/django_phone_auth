# Django Phone Auth

Пример реферальной системы на Django, с авторизацией по номеру телефона.
## Установка

Клонируйте проект в свою рабочую директорию.

```bash
git clone git@github.com:Mirrormsk/django_phone_auth.git
```

## Docker
Переименуйте файл `.env.example` в `.env.docker` и укажите значения для переменных.
Для запуска через Docker выполните команду: 

```bash
docker compose up --build
```

## Локальный запуск
Создайте виртуальное окружение и активируйте его

```bash
python3 -m venv venv
source venv/bin/activate
```
Установите зависимости:

```bash
pip install -r requirements.txt
```

Переименуйте файл `.env.example` в `.env` и укажите необходимые переменные. 


Примените миграции:

```bash
python3 manage.py migrate
```


Для локального запуска выполните команду


```bash
python manage.pu runserver
```

## Настройка SMS-шлюза
Для реализации собственного класса для отправки смс унаследуйте его от базового класса `users.services.sms.AbstractSMSService`, и реализуйте метол `send_sms`. Укажите адрес до вашего класса в файлу `.env` в переменной `SMS_SERVICE`:

```
SMS_SERVICE=users.services.sms_providers.smsc.smsc_api.SMSCService
```

В этом примере указан реализованный в проекте шлюз отправки смс - [SMSC](https://smsc.ru/). 
Для его работы необходимы следующие переменные в файле`.env`:
```
SMSC_LOGIN=login
SMSC_PASSWORD=password
SMSC_POST=0
SMSC_HTTPS=0
SMSC_CHARSET=utf-8
SMSC_DEBUG=0
```

Для демонстрации можно использовать класс `FakeSMSService`, который выводит данные в консоль:

```env
SMS_SERVICE=users.services.sms.FakeSMSService
```

Настройка тайм-аута для отправки нового кода подтверждения задается в переменной `SMS_VERIFICATION_RESEND_TIMEOUT` в секундах:

```env
SMS_VERIFICATION_RESEND_TIMEOUT=10
```

## Документация
Документация Swagger доступна по адресу `/docs`.

## Использование

1. Отправьте POST запрос на адрес `/api/login/`. Пример запроса:
```json
{
  "phone": "79999999999"
}
```
2. Полученный код подтверждения вместе с телефоном нужно отправить POST запрос на `/api/verify`:

```json
{
    "phone": "+79299114424",
    "otp_code": "9987"
}
```
3. Если у вас есть реферальный код, то можно ввести его отправив POST запрос по адресу `/users/<pk>/input_invite/`:

```json
{
    "invite_code": "dIgsog"
}
```
4. Информацию о профиле, а также свой реферальный код можно посмотреть в `/users/pk/`


## Пример работы

Для примера работы с фронтендом реализован эндпоинт `/login`, в котором можно 
ввести номер телефона, и получить проверочный код. В случае правильного ввода будет показан access-токен.

