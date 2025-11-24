from django.http import JsonResponse
from django.conf import settings
import redis
import json
import time
from . import parser
import pickle as pkl
import io

redis_instance = redis.StrictRedis(host=settings.REDIS_HOST,
                                   port=settings.REDIS_PORT, db=0)

class Constants:
    UPDATE_PERIOD = 60 * 10

class DataBaseKeys:
    LAST_UPDATE = 'last_update'
    CALENDAR = 'calendar'
    CLUBS = 'clubs'
    STANDINGS = 'standings'
    STANDINGS_HOME = 'standings_home'
    STANDINGS_ROAD = 'standings_road'
    PERIOD_1 = 'period_1'
    PERIOD_2 = 'period_2'
    PERIOD_3 = 'period_3'
    POWERPLAY = 'powerplay'

def redis_get_json(key):
    res = redis_instance.get(key)
    if res:
        return json.loads(res)
    return res

def redis_set_json(key, value):
    redis_instance.set(key, json.dumps(value))

def update_db():
    cur_time = time.time()
    last_update = redis_get_json(DataBaseKeys.LAST_UPDATE)
    if last_update is not None:
        last_update = float(last_update['time'])

    if last_update is None or cur_time - last_update > Constants.UPDATE_PERIOD:
        calendar = parser.parse_calendar()
        clubs = parser.parse_clubs()

        standings = parser.parse_standings_all()
        standings_home = parser.parse_standings_home()
        standings_road = parser.parse_standings_road()

        period_1 = parser.parse_period_1()
        period_2 = parser.parse_period_2()
        period_3 = parser.parse_period_3()

        powerplay = parser.parse_powerplay()

        redis_set_json(DataBaseKeys.LAST_UPDATE, {'time': cur_time})
        redis_set_json(DataBaseKeys.CALENDAR, calendar)
        redis_set_json(DataBaseKeys.CLUBS, clubs)

        redis_set_json(DataBaseKeys.STANDINGS, standings)
        redis_set_json(DataBaseKeys.STANDINGS_HOME, standings_home)
        redis_set_json(DataBaseKeys.STANDINGS_ROAD, standings_road)

        redis_set_json(DataBaseKeys.PERIOD_1, period_1)
        redis_set_json(DataBaseKeys.PERIOD_2, period_2)
        redis_set_json(DataBaseKeys.PERIOD_3, period_3)

        redis_set_json(DataBaseKeys.POWERPLAY, powerplay)
        

def calendar(request):
    update_db()
    calendar = redis_get_json(DataBaseKeys.CALENDAR)
    return JsonResponse(calendar)


def clubs(request):
    update_db()
    clubs = redis_get_json(DataBaseKeys.CLUBS)
    return JsonResponse(clubs)


def clubs_compare(request):
    update_db()
    club1 = request.GET.get('left_team')
    club2 = request.GET.get('right_team')

    # ---filipchuk.al 24.11.2025---
    # Добавлена проверка на отсутствие параметров и автоматическое добавление слэша к названию команды
    #if not club1.endswith('/'):
    #   club1 = club1 + '/'
    # if not club2.endswith('/'):
    #   club2 = club2 + '/'
    if not club1 or not club2:
        return JsonResponse(
            {"error": "Parameters 'left_team' and 'right_team' are required."},
            status=400
        )

    # Добавляем слэш, если нет
    if not club1.endswith('/'):
        club1 += '/'
    if not club2.endswith('/'):
        club2 += '/'
    # -----------------------------

    clubs = redis_get_json(DataBaseKeys.CLUBS)

    standings = redis_get_json(DataBaseKeys.STANDINGS)
    standings_home = redis_get_json(DataBaseKeys.STANDINGS_HOME)
    standings_road = redis_get_json(DataBaseKeys.STANDINGS_ROAD)

    period_1 = redis_get_json(DataBaseKeys.PERIOD_1)
    period_2 = redis_get_json(DataBaseKeys.PERIOD_2)
    period_3 = redis_get_json(DataBaseKeys.PERIOD_3)

    powerplay = redis_get_json(DataBaseKeys.POWERPLAY)

    result = {}
    for key, value in zip(
        [
            DataBaseKeys.STANDINGS,
            DataBaseKeys.STANDINGS_HOME,
            DataBaseKeys.STANDINGS_ROAD,
            DataBaseKeys.PERIOD_1,
            DataBaseKeys.PERIOD_2, 
            DataBaseKeys.PERIOD_3,
            DataBaseKeys.POWERPLAY
        ],
        [
            standings,
            standings_home,
            standings_road,
            period_1,
            period_2,
            period_3,
            powerplay
        ]
    ):  
        # ---filipchuk.al 24.11.2025---
        # Используем .get() для безопасного получения данных без ошибок при отсутствии ключа
        #result[key] = {
        #   'left_team': value[club1],
        #   'right_team': value[club2]
        #}
        result[key] = {
            'left_team': value.get(club1),
            'right_team': value.get(club2)
        }
        # -----------------------------

    return JsonResponse(result)