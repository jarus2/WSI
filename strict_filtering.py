# Dodatkowa filtracja danych
def apply_strict_filtering(df, ulubiona_kuchnia, max_cena, max_odleglosc):
    filtrowane = df.copy()

    if ulubiona_kuchnia:
        filtrowane = filtrowane[filtrowane['kuchnia'].str.lower() == ulubiona_kuchnia]

    filtrowane = filtrowane[
        (filtrowane['odleglosc_km'] <= max_odleglosc) &
        (filtrowane['cena'] <= max_cena)
    ]

    return filtrowane

def show_filtered_results(df):
    if df.empty:
        print("\nBrak restauracji spełniających ścisłe kryteria.")
    else:
        print("\nRestauracje spełniające ścisłe kryteria:")
        for _, row in df.iterrows():
            print(f"- {row['nazwa']} | Kuchnia: {row['kuchnia']} | Cena: {row['cena']} zł | "
                  f"Ocena: {row['ocena']} | Odległość: {row['odleglosc_km']} km")
