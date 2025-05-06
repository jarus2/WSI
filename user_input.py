# pobieranie preferencji użytkownika
def get_user_preferences():
    ulubiona_kuchnia = input("Jaka kuchnia Cię interesuje? (np. włoska, sushi) [ENTER = dowolna]: ").strip().lower()
    odl_input = input("Maksymalna odległość (km) [ENTER = brak limitu]: ").strip()
    cena_input = input("Maksymalna cena (zł) [ENTER = brak limitu]: ").strip()
    ocena_pref = input("Preferowana jakość oceny? [każda / dobra / bardzo dobra]: ").strip().lower()

    # obsługa ENTER w inputach liczbowych
    try:
        max_odleglosc = float(odl_input) if odl_input else float('inf')
    except ValueError:
        max_odleglosc = float('inf')

    try:
        max_cena = float(cena_input) if cena_input else float('inf')
    except ValueError:
        max_cena = float('inf')

    return ulubiona_kuchnia, max_cena, max_odleglosc, ocena_pref
