# main.py
import database
import fuel_parser
import os

def clear_screen():
    """Очищает экран консоли."""
    os.system('cls' if os.name == 'nt' else 'clear')

def get_float_input(prompt):
    """Получает от пользователя число с плавающей точкой, обрабатывая ошибки."""
    while True:
        try:
            return float(input(prompt).replace(',', '.'))
        except ValueError:
            print("Ошибка! Пожалуйста, введите число.")

def get_int_input(prompt):
    """Получает от пользователя целое число, обрабатывая ошибки."""
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print("Ошибка! Пожалуйста, введите целое число.")

def handle_add_fuel():
    """Обрабатывает добавление записи о заправке."""
    clear_screen()
    print("--- Добавление записи о заправке ---")
    
    # Пытаемся получить цены автоматически
    prices = fuel_parser.get_belarus_fuel_prices()
    selected_price = 0

    if prices:
        print("\nВыберите тип топлива:")
        fuel_options = list(prices.keys())
        for i, fuel in enumerate(fuel_options):
            print(f"{i + 1}. {fuel} - {prices[fuel]} BYN")
        print("0. Ввести цену вручную")
        
        choice = get_int_input("\nВаш выбор: ")
        if 0 < choice <= len(fuel_options):
            selected_price = float(prices[fuel_options[choice - 1]])
    
    if selected_price == 0:
        selected_price = get_float_input("Введите цену за литр: ")

    last_odo = database.get_latest_odometer()
    print(f"\nПоследний известный пробег: {last_odo} км")
    odometer = get_int_input("Введите текущий пробег (км): ")
    liters = get_float_input("Введите количество литров: ")
    
    total_cost = database.add_fuel_record(odometer, liters, selected_price)
    print(f"\n✅ Запись о заправке добавлена! Сумма: {total_cost} BYN")
    input("\nНажмите Enter, чтобы вернуться в меню...")

def handle_add_part():
    """Обрабатывает добавление записи о замене запчасти."""
    clear_screen()
    print("--- Добавление записи о замене запчасти ---")
    
    part_name = input("Введите название запчасти (например, 'Масло ДВС' или 'Фильтр воздушный'): ")
    last_odo = database.get_latest_odometer()
    print(f"\nПоследний известный пробег: {last_odo} км")
    odometer = get_int_input("Введите пробег на момент замены: ")
    price = get_float_input("Введите стоимость запчасти (и работы): ")
    
    lifespan_str = input("Введите ресурс запчасти в км (оставьте пустым, если нет): ")
    lifespan = int(lifespan_str) if lifespan_str.isdigit() else None
    
    notes = input("Введите заметки (необязательно): ")

    database.add_part_record(part_name, odometer, price, lifespan, notes)
    print(f"\n✅ Запись о замене '{part_name}' добавлена!")
    input("\nНажмите Enter, чтобы вернуться в меню...")

def handle_reminders():
    """Показывает напоминания о замене."""
    clear_screen()
    print("--- Напоминания о замене запчастей ---")
    
    last_odo = database.get_latest_odometer()
    print(f"Последний известный пробег: {last_odo} км")
    current_odometer = get_int_input("Введите ТЕКУЩИЙ пробег для проверки: ")
    
    reminders = database.get_reminders(current_odometer)
    
    if not reminders:
        print("\n👍 Пока нет срочных напоминаний.")
    else:
        print("\nВнимание:")
        for r in reminders:
            print(f"- {r}")
            
    input("\nНажмите Enter, чтобы вернуться в меню...")

def handle_analysis():
    """Показывает анализ затрат."""
    clear_screen()
    print("--- Полный анализ затрат на автомобиль ---")
    
    stats = database.get_full_analysis()
    
    print(f"\n⛽ Затраты на топливо: {stats['total_fuel']} BYN")
    print(f"🛠️ Затраты на запчасти и работы: {stats['total_parts']} BYN")
    print("-" * 30)
    print(f"💰 ОБЩИЕ ЗАТРАТЫ: {stats['grand_total']} BYN")
    
    input("\nНажмите Enter, чтобы вернуться в меню...")


def main_menu():
    """Главное меню приложения."""
    database.init_db() # Убедимся, что БД и таблицы созданы
    while True:
        clear_screen()
        print("===== Ваш Автомобильный Ассистент v1.0 =====")
        print("\nПоследний известный пробег:", database.get_latest_odometer(), "км")
        print("\nВыберите действие:")
        print("1. ⛽ Добавить заправку (с авто-ценой)")
        print("2. 🛠️ Добавить замену запчасти")
        print("3. ❗ Посмотреть напоминания по замене")
        print("4. 📊 Показать полный анализ затрат")
        print("0. 🚪 Выход")

        choice = input("\n> ")
        if choice == '1':
            handle_add_fuel()
        elif choice == '2':
            handle_add_part()
        elif choice == '3':
            handle_reminders()
        elif choice == '4':
            handle_analysis()
        elif choice == '0':
            print("До встречи на дорогах!")
            break
        else:
            print("Неверный выбор, попробуйте снова.")
            input("Нажмите Enter...")


if __name__ == '__main__':
    main_menu()