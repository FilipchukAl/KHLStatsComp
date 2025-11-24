from bs4 import BeautifulSoup
import requests
# ---filipchuk.al 24.11.2025---
# Добавил библеотеку curl_cffi для обхода блокировок сайта
from curl_cffi import requests
# -----------------------------
from collections import namedtuple, Counter
import pickle as pkl

# ---filipchuk.al 24.11.2025---
# Настроил Django окружение и добавил путь к проекту для корректного импорта модулей
import os
import sys
import django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()
# -----------------------------

class GameFields:
    GAME_ID = 'game_id'
    LEFT_TEAM = 'left_team'
    RIGHT_TEAM = 'right_team'
    DATE = 'date'
    GAME_NO = 'game_no'
    TIME = 'time'
    PLACE = 'place'

class TeamFields:
    TEAM_ID = 'team_id'
    TEAM = 'team'
    TEAM_UNIQUE = 'team_unique'
    CITY = 'city'
    LOGO = 'logo'

BETTER = {
    '№': '',
    'И': '',
    'В': 'more',
    'ВО': 'more',
    'ВБ': 'more',
    'П': 'less',
    'ПО': 'less',
    'ПБ': 'less',
    'О': 'more',
    'Ибз': 'less',
    'Ибп': 'more',
    'ЗШ': 'more',
    'ПШ': 'less',
    'Штр': 'less',
    'ШтрС': 'more',
    'ВПР': '',
    'ВПР/И': '',
    'ВППВ': 'less',
    'ВППВ/И': 'less',
    'Н': '',
    'Бол': 'more',
    'ШБ': 'more',
    '%Б': 'more',
    'ПШБ': 'less',
    'ВПБ': 'more',
    'ВПБ/И': 'more',
    'Мен': 'less',
    'ПШМ': 'less',
    '%М': 'more',
    'ШМ': 'more',
    'ВПМ': 'less',
    'ВПМ/И': 'less',
    # Добавились Отборы шайбы
    # 'ОТБ': 'more'
}


def parse_team(team_doc):
    team, city = [x.contents[0].strip() for x in team_doc.find_all('p')]
    return {
        TeamFields.TEAM_ID: team_doc['href'],
        TeamFields.TEAM: team,
        TeamFields.CITY: city,
        TeamFields.TEAM_UNIQUE: team if team != 'Динамо' else f'{team} {"МН" if city =="Минск" else "M"}',
        TeamFields.LOGO: team_doc.find('img')['src']
    }

def parse_game_info(info_doc):
    return [x.contents[0].strip() for x in info_doc.find_all('p')]

def parse_future_games_day(games_day_doc):
    date = games_day_doc.find_all('time')[0].contents[0].strip()
    games = games_day_doc.find_all('div', {'class': 'card-game card-game--calendar'})
    result = []
    for game in games:
        game_id = game.find('a')['href'].rsplit('/', 2)[0]
        game_no, time, place = parse_game_info(game.find('div', {'class': 'card-game__center'}))
        result.append({
            GameFields.GAME_ID: game_id,
            GameFields.LEFT_TEAM: parse_team(game.find('a', {'class': 'card-game__club card-game__club_left'})),
            GameFields.RIGHT_TEAM: parse_team(game.find('a', {'class': 'card-game__club card-game__club_right'})),
            GameFields.DATE: date,
            GameFields.TIME: time,
            GameFields.GAME_NO: game_no,
            GameFields.PLACE: place
        })
    return result

def parse_calendar():
    # ---filipchuk.al 24.11.2025---
    # Заменил requests на curl_cffi для обхода блокировок сайта
    # response = requests.get('https://www.khl.ru/calendar/')
    response = requests.get('https://www.khl.ru/calendar/', impersonate="chrome136", timeout=10)
    # -----------------------------
    if not response.status_code == 200:
        return []
    doc = response.text

    soup = BeautifulSoup(doc, 'html.parser')
    calendar = soup.find('div', {'class': 'calendary-body'})
    games_day = calendar.find_all('div', {'class': 'calendary-body__item games_featured'})
    result = []
    for x in games_day:
        result.extend(parse_future_games_day(x))
    return {'calendar': result}


def parse_clubs():
    # ---filipchuk.al 24.11.2025---
    # Заменил requests на curl_cffi для обхода блокировок сайта
    # response = requests.get('https://www.khl.ru/clubs/')
    response = requests.get('https://www.khl.ru/clubs/', impersonate="chrome136", timeout=10)
    # -----------------------------
    if not response.status_code == 200:
        return []
    doc = response.text

    soup = BeautifulSoup(doc, 'html.parser')
    clubs = soup.find_all('div', {'class': 'cardClub-card'})
    result = []
    for club in clubs:
        result.append(parse_team(club.find('a')))
    return {'clubs': result}


def parse_table(address, need_pos=True):
    # ---filipchuk.al 24.11.2025---
    # Заменил requests на curl_cffi для обхода блокировок сайта
    # response = requests.get(address)
    response = requests.get(address, impersonate="chrome136", timeout=10)
    # -----------------------------
    if not response.status_code == 200:
        return []
    doc = response.text

    soup = BeautifulSoup(doc, 'html.parser')
    header = soup.find('thead')
    standings = soup.find('tbody')
    
    names = [x['title'] for x in header.find_all('th')]
    names = [name if (name != '№' and name != 'Номер') else 'Место' for name in names]
    aliases = [x.find('p').contents[0] for x in header.find_all('th')]

    result = {}

    for row in standings.find_all('tr'):
        club = row.find('td').find('a')['href'].split('/')[-2]
        club = f'/clubs/{club}/'
        values = [x.find('p').contents[0] for x in row.find_all('th')]

        stats = []
        for name, alias, value in zip(names[1:], aliases[1:], values):
            if alias == 'Клуб':
                continue

            if alias == '№' and not need_pos:
                continue

            if ':' in value:
                value = str(float(value.split(':')[0]) + round(float(value.split(':')[1]) / 60, 1))

            stats.append({
                'key': alias,
                'value': value,
                'name': name,
                # ---filipchuk.al 24.11.2025---
                # Изменил BETTER.get добавление нового элемента в словарь не крашит приложение
                'better': BETTER.get(alias, None)
                # -----------------------------
            })

        result[club] = stats
    
    return result

def parse_standings_all():
    return parse_table('https://www.khl.ru/stat/teams/1154/')

def parse_standings_home():
    return parse_table('https://www.khl.ru/stat/teams/1154/home/')

def parse_standings_road():
    return parse_table('https://www.khl.ru/stat/teams/1154/road/')

def parse_period_1():
    return parse_table('https://www.khl.ru/stat/teams/1154/first-period/')

def parse_period_2():
    return parse_table('https://www.khl.ru/stat/teams/1154/second-period/')

def parse_period_3():
    return parse_table('https://www.khl.ru/stat/teams/1154/third-period/')


def parse_powerplay():
    return parse_table('https://www.khl.ru/stat/teams/1154/powerplay-gf/', False)