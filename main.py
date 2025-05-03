# podstawowy pagerank bez preferencji użytkownika
# ze niewłaściwymi fuzzy sets
# do testów

import numpy as np
import skfuzzy as fuzz # pip install scikit-fuzzy
import pandas as pd # pip install pandas
import networkx as nx # pip install networkx

# === KROK 1: Wczytaj dane ===
df = pd.read_csv("restauracje.txt")

# === KROK 2: Fuzzy logic ===
cena_range = np.arange(0, 201, 1)
ocena_range = np.arange(0, 5.1, 0.1)
odl_range = np.arange(0, 11, 0.1)

tania = fuzz.trimf(cena_range, [0, 0, 60])
srednia = fuzz.trimf(cena_range, [40, 80, 120])
droga = fuzz.trimf(cena_range, [100, 150, 200])

niska = fuzz.trimf(ocena_range, [0, 0, 3.5])
srednia_o = fuzz.trimf(ocena_range, [3.0, 4.0, 4.5])
wysoka = fuzz.trimf(ocena_range, [4.2, 5.0, 5.0])

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
        
        'ocena_niska': fuzz.interp_membership(ocena_range, niska, ocena),
        'ocena_srednia': fuzz.interp_membership(ocena_range, srednia_o, ocena),
        'ocena_wysoka': fuzz.interp_membership(ocena_range, wysoka, ocena),
        
        'blisko': fuzz.interp_membership(odl_range, blisko, odl),
        'srednio_daleko': fuzz.interp_membership(odl_range, srednio_daleko, odl),
        'daleko': fuzz.interp_membership(odl_range, daleko, odl),
    })

fuzzy_df = df.join(df.apply(fuzzify_row, axis=1))

# === KROK 3: Tworzenie grafu ===
def podobienstwo_fuzzy(row1, row2):
    cechy = ['tania', 'srednia_cena', 'droga',
             'ocena_niska', 'ocena_srednia', 'ocena_wysoka',
             'blisko', 'srednio_daleko', 'daleko']
    return sum(row1[c] * row2[c] for c in cechy)

G = nx.DiGraph()
for idx, row in fuzzy_df.iterrows():
    G.add_node(row['nazwa'], kuchnia=row['kuchnia'])

for i, row1 in fuzzy_df.iterrows():
    for j, row2 in fuzzy_df.iterrows():
        if i != j:
            waga = podobienstwo_fuzzy(row1, row2)
            if waga > 0.1:
                G.add_edge(row1['nazwa'], row2['nazwa'], weight=waga)

# === KROK 4: Obliczenie PageRank ===
pagerank_scores = nx.pagerank(G, alpha=0.85, weight='weight')

# === KROK 5: Preferencje użytkownika ===
ulubiona_kuchnia = input("Jaka kuchnia Cię interesuje? (np. włoska, sushi, indyjska): ").lower().strip()
max_odleglosc = float(input("Maksymalna odległość w km: "))
max_cena = float(input("Maksymalna cena w zł: "))

# Filtrowanie restauracji
filtrowane = fuzzy_df[
    (fuzzy_df['kuchnia'].str.lower() == ulubiona_kuchnia) &
    (fuzzy_df['odleglosc_km'] <= max_odleglosc) &
    (fuzzy_df['cena'] <= max_cena)
]

# Dodaj wynik PageRanku
filtrowane['pagerank'] = filtrowane['nazwa'].map(pagerank_scores)

# Sortowanie wg PageRank
rekomendacje = filtrowane.sort_values(by='pagerank', ascending=False)

print("\n📌 Najlepsze restauracje dopasowane do Twoich preferencji:\n")
for i, row in rekomendacje.iterrows():
    print(f"⭐ {row['nazwa']} | Kuchnia: {row['kuchnia']} | Cena: {row['cena']} zł | Ocena: {row['ocena']} | Odległość: {row['odleglosc_km']} km | PageRank: {row['pagerank']:.4f}")

