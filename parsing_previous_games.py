from curl_cffi import requests
from bs4 import BeautifulSoup
import pandas as pd

# Ввод команд с клавиатуры
team_a = input("Введите первую команду: ").strip()
team_b = input("Введите вторую команду: ").strip()

session = requests.Session()

# Функция парсинга одной страницы
def parse_page(url):
    response = session.get(url, impersonate="chrome136", timeout=10)
    soup = BeautifulSoup(response.text, "html.parser")
    
    sections = soup.find_all("div", class_="calendar__section date")
    
    data = []
    for section in sections:
        date = section.get("data-date")
        events = section.find_all("div", class_="calendar__event")
        
        for event in events:
            clubs = event.find_all("h6", class_="calendar__club-name")
            score_divs = event.find_all("div", class_="calendar__check-number")
            
            # Берем только реальные счета (в span цифра)
            active_scores = [s for s in score_divs if s.span and s.span.get_text(strip=True).isdigit()]
            
            if len(clubs) == 2 and len(active_scores) == 2:
                team1 = clubs[0].get_text(strip=True)
                team2 = clubs[1].get_text(strip=True)
                score1 = active_scores[0].span.get_text(strip=True)
                score2 = active_scores[1].span.get_text(strip=True)
                
                data.append({
                    "date": date,
                    "team1": team1,
                    "team2": team2,
                    "score": f"{score1}:{score2}"
                })
    return data

# Основная функция для сезона
def parse_season(season_url, max_pages):
    all_data = []
    for page in range(1, max_pages + 1):
        url = f"{season_url}/?PAGEN_3={page}"
        page_data = parse_page(url)
        if not page_data:
            continue
        all_data.extend(page_data)
    return all_data

# Сезоны и количество страниц
seasons = {
    "2024-2025": ("https://hctorpedo.ru/season/matches/2024-2025-regular", 40),
    "2025-2026": ("https://hctorpedo.ru/season/matches/2025-2026-regular", 38)
}

# Сбор всех данных
all_matches = []
for season_name, (base_url, pages) in seasons.items():
    for page in range(1, pages + 1):
        url = f"{base_url}/?PAGEN_3={page}"
        season_data = parse_page(url)
        for match in season_data:
            match["season"] = season_name
        all_matches.extend(season_data)

# Создаем DataFrame и удаляем дубликаты
df = pd.DataFrame(all_matches)
df.drop_duplicates(subset=["date", "team1", "team2"], inplace=True)
df.reset_index(drop=True, inplace=True)

# Фильтр матчей между двумя командами (без учета регистра)
matches = df[
    ((df['team1'].str.lower().str.strip() == team_a.lower()) &
     (df['team2'].str.lower().str.strip() == team_b.lower())) |
    ((df['team1'].str.lower().str.strip() == team_b.lower()) &
     (df['team2'].str.lower().str.strip() == team_a.lower()))
]

print(matches)