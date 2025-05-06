import numpy as np
import skfuzzy as fuzz
import pandas as pd
import networkx as nx

# === KROK 1: Wczytaj dane ===
df = pd.read_csv("restauracje.txt")

# === KROK 2: Rozmycie cech ===
cena_range = np.arange(0, 201, 1)
ocena_range = np.arange(0, 5.1, 0.1)
odl_range = np.arange(0, 11, 0.1)

# Funkcje przynależności
tania = fuzz.trimf(cena_range, [0, 0, 60])
srednia = fuzz.trimf(cena_range, [40, 80, 120])
droga = fuzz.trimf(cena_range, [100, 150, 200])

def mu_ocena_niska(x):
    if x <= 2.0:
        return 1
    elif 2.0 < x < 3.5:
        return (3.5 - x) / 1.5
    else:
        return 0

def mu_ocena_dobra(x):
    if x <= 2.5:
        return 0
    elif 2.5 < x < 4.0:
        return (x - 2.5) / 1.5
    elif 4.0 <= x < 4.5:
        return 1
    elif 4.5 <= x < 5.0:
        return (5.0 - x) / 0.5
    else:
        return 0

def mu_ocena_bardzo_dobra(x):
    if x <= 3.5:
        return 0
    elif 3.5 < x < 5.0:
        return (x - 3.5) / 1.5
    else:
        return 1


blisko = fuzz.trimf(odl_range, [0, 0, 2.5])
srednio_daleko = fuzz.trimf(odl_range, [1.5, 4, 6])
daleko = fuzz.trimf(odl_range, [5, 8, 10])

def fuzzify_row(row):
    cena = row['cena']
    ocena = row['ocena']
    odl = row['odleglosc_km']
    
    return pd.Series({
        'tania': fuzz.interp_membership(cena_range, tania, cena),
        'srednia_cena': fuzz.interp_membership(cena_range, srednia, cena),
        'droga': fuzz.interp_membership(cena_range, droga, cena),
        
        'ocena_niska': mu_ocena_niska(ocena),
        'ocena_dobra': mu_ocena_dobra(ocena),
        'ocena_bardzo_dobra': mu_ocena_bardzo_dobra(ocena),
        
        'blisko': fuzz.interp_membership(odl_range, blisko, odl),
        'srednio_daleko': fuzz.interp_membership(odl_range, srednio_daleko, odl),
        'daleko': fuzz.interp_membership(odl_range, daleko, odl),
    })

# Tworzymy ramkę z fuzzy cechami
fuzzy_df = df.join(df.apply(fuzzify_row, axis=1))

# === KROK 3: Budowa grafu ===
def podobienstwo_fuzzy(row1, row2):
    cechy = ['tania', 'srednia_cena', 'droga',
         'ocena_niska', 'ocena_dobra', 'ocena_bardzo_dobra',
         'blisko', 'srednio_daleko', 'daleko']
    
    # Podstawowe podobieństwo na podstawie cech
    podobienstwo_cech = sum(row1[c] * row2[c] for c in cechy)

    # Uwzględnienie kuchni
    if row1['kuchnia'].lower() == row2['kuchnia'].lower():
        podobienstwo_cech *= 1.2  
    else:
        podobienstwo_cech *= 0.5  
    
    return podobienstwo_cech



G = nx.DiGraph()

for idx, row in fuzzy_df.iterrows():
    G.add_node(row['nazwa'], kuchnia=row['kuchnia'])

for i, row1 in fuzzy_df.iterrows():
    for j, row2 in fuzzy_df.iterrows():
        if i != j:
            waga = podobienstwo_fuzzy(row1, row2)
            if waga > 0.1:
                G.add_edge(row1['nazwa'], row2['nazwa'], weight=waga)

# === KROK 4: Preferencje użytkownika ===
ulubiona_kuchnia = input("Jaka kuchnia Cię interesuje? (np. włoska, sushi) [ENTER = dowolna]: ").strip().lower()
odl_input = input("Maksymalna odległość (km) [ENTER = brak limitu]: ").strip()
cena_input = input("Maksymalna cena (zł) [ENTER = brak limitu]: ").strip()

try:
    max_odleglosc = float(odl_input) if odl_input else float('inf')
except ValueError:
    max_odleglosc = float('inf')

try:
    max_cena = float(cena_input) if cena_input else float('inf')
except ValueError:
    max_cena = float('inf')

# === KROK 5: Personalizowany wektor teleportacji ===
def stopien_preferencji(row):
    score = 0
    if row['kuchnia'].lower() == ulubiona_kuchnia:
        score += 0.5
    if row['cena'] <= max_cena:
        score += 0.3
    if row['odleglosc_km'] <= max_odleglosc:
        score += 0.2
    return score

personalizacja = {
    row['nazwa']: stopien_preferencji(row)
    for idx, row in fuzzy_df.iterrows()
}

suma = sum(personalizacja.values())
personalization = {k: v / suma for k, v in personalizacja.items()} if suma > 0 else None

# === KROK 6: Obliczenie PageRank ===
pagerank_scores = nx.pagerank(G, alpha=0.85, personalization=personalization, weight='weight')

# === KROK 7: Filtracja wyników wg preferencji ===
filtrowane = fuzzy_df.copy()
if ulubiona_kuchnia:
    filtrowane = filtrowane[filtrowane['kuchnia'].str.lower() == ulubiona_kuchnia]
filtrowane = filtrowane[
    (filtrowane['odleglosc_km'] <= max_odleglosc) &
    (filtrowane['cena'] <= max_cena)
]


filtrowane['pagerank'] = filtrowane['nazwa'].map(pagerank_scores)

# === KROK 8: Rekomendacje ===
rekomendacje = filtrowane.sort_values(by='pagerank', ascending=False)

print("\n📌 Najlepsze restauracje dla Ciebie:\n")
if rekomendacje.empty:
    print("⚠️ Nie znaleziono restauracji spełniających kryteria.")
else:
    for i, row in rekomendacje.iterrows():
        print(f"⭐ {row['nazwa']} | Kuchnia: {row['kuchnia']} | Cena: {row['cena']} zł | "
              f"Ocena: {row['ocena']} | Odległość: {row['odleglosc_km']} km | PageRank: {row['pagerank']:.4f}")
