# fuel_parser.py
import requests
from bs4 import BeautifulSoup
import logging

# Отключаем слишком подробные логи от requests
logging.basicConfig(level=logging.WARNING)

# URL, на котором обычно есть актуальные цены от Белнефтехим
URL = "https://www.belneftekhim.by/company/press-center/petroleum-products-price/"

def get_belarus_fuel_prices():
    """
    Парсит сайт Белнефтехим для получения актуальных цен на топливо.
    Возвращает словарь вида {'АИ-92-К5-Евро': '2.36', ...} или пустой словарь при ошибке.
    """
    print("⏳ Получаю актуальные цены на топливо с сайта Белнефтехим...")
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(URL, headers=headers, timeout=10)
        response.raise_for_status()  # Проверка на ошибки HTTP (вроде 404, 500)

        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Ищем таблицу с ценами. Этот селектор может измениться, если сайт поменяет структуру!
        price_table = soup.find('table', class_='table-price')
        
        if not price_table:
            print("❌ Не удалось найти таблицу с ценами на странице. Возможно, структура сайта изменилась.")
            return {}

        prices = {}
        # Ищем все строки в теле таблицы
        rows = price_table.find('tbody').find_all('tr')
        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 2:
                # Берем название из первой колонки и цену из второй
                fuel_name = cols[0].text.strip()
                fuel_price = cols[1].text.strip()
                if fuel_name and fuel_price:
                    prices[fuel_name] = fuel_price
        
        if prices:
            print("✅ Цены успешно получены!")
            return prices
        else:
            print("❌ Не удалось извлечь данные из таблицы.")
            return {}

    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка сети при получении цен: {e}")
        return {}
    except Exception as e:
        print(f"❌ Произошла непредвиденная ошибка при парсинге цен: {e}")
        return {}

if __name__ == '__main__':
    # Для теста можно запустить этот файл напрямую
    current_prices = get_belarus_fuel_prices()
    if current_prices:
        for fuel, price in current_prices.items():
            print(f"{fuel}: {price} BYN")