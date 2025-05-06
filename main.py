import pandas as pd
import networkx as nx
from fuzzy_logic import fuzzify_row
from fuzzy_graph import build_graph
from user_input import get_user_preferences
from strict_filtering import apply_strict_filtering, show_filtered_results

# ===== dane =====
df = pd.read_csv("restauracje.txt")
fuzzy_df = df.join(df.apply(fuzzify_row, axis=1))

# ===== preferencje użytkownika =====
ulubiona_kuchnia, max_cena, max_odleglosc, ocena_pref = get_user_preferences()

# ===== budowa grafu i personalizacja =====
G, preferencje = build_graph(fuzzy_df, ulubiona_kuchnia, max_cena, max_odleglosc, ocena_pref)

personalization = {node: 0 for node in G.nodes()}
personalization['Użytkownik'] = 1.0
pagerank_scores = nx.pagerank(G, alpha=0.85, personalization=personalization, weight='weight')
pagerank_scores.pop('Użytkownik', None)

# ===== filtracja i wyniki =====
fuzzy_df['pagerank'] = fuzzy_df['nazwa'].map(pagerank_scores)
rekomendacje = fuzzy_df.sort_values(by='pagerank', ascending=True)

print("\n Najlepsze restauracje:\n")
if rekomendacje.empty:
    print("Nie znaleziono restauracji.")
else:
    for _, row in rekomendacje.iterrows():
        print(f"- {row['nazwa']} | Kuchnia: {row['kuchnia']} | Cena: {row['cena']} zł | "
              f"Ocena: {row['ocena']} | Odległość: {row['odleglosc_km']} km | PageRank: {row['pagerank']:.4f}")


# ===== dodatkowa opcjonalna filtracja =====
filtruj = input("\nCzy wyświetlić tylko restauracje ściśle spełniające kryteria? (tak/nie): ").strip().lower()
if filtruj == 'tak':
    filtrowane = apply_strict_filtering(fuzzy_df, ulubiona_kuchnia, max_cena, max_odleglosc)
    show_filtered_results(filtrowane)
