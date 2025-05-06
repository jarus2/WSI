import networkx as nx


def podobienstwo_fuzzy(row1, row2):
    cechy = ['tania', 'srednia_cena', 'droga',
             'ocena_niska', 'ocena_dobra', 'ocena_bardzo_dobra',
             'blisko', 'srednio_daleko', 'daleko']

    podobienstwo_cech = sum(row1[c] * row2[c] for c in cechy)

    if row1['kuchnia'].lower() == row2['kuchnia'].lower():
        podobienstwo_cech *= 1.2
    else:
        podobienstwo_cech *= 0.5

    return podobienstwo_cech



def stopien_preferencji(row, ulubiona_kuchnia, max_cena, max_odleglosc, ocena_pref):
    score = 0
    if ulubiona_kuchnia and row['kuchnia'].lower() == ulubiona_kuchnia:
        score += 0.9
    if row['cena'] <= max_cena:
        score += 0.7
    if row['odleglosc_km'] <= max_odleglosc:
        score += 0.5

    if ocena_pref == 'dobra' and row['ocena_dobra'] < 0.5 and row['ocena_bardzo_dobra'] < 0.5:
        return 0
    elif ocena_pref == 'bardzo dobra' and row['ocena_bardzo_dobra'] < 0.5:
        return 0

    return score



def build_graph(fuzzy_df, ulubiona_kuchnia, max_cena, max_odleglosc, ocena_pref):
    G = nx.DiGraph()

    for _, row in fuzzy_df.iterrows():
        G.add_node(row['nazwa'], kuchnia=row['kuchnia'])

    for i, row1 in fuzzy_df.iterrows():
        for j, row2 in fuzzy_df.iterrows():
            if i != j:
                waga = podobienstwo_fuzzy(row1, row2)
                if waga > 0.1:
                    G.add_edge(row1['nazwa'], row2['nazwa'], weight=waga)

    G.add_node('Użytkownik')
    preferencje = {}

    for _, row in fuzzy_df.iterrows():
        pref = stopien_preferencji(row, ulubiona_kuchnia, max_cena, max_odleglosc, ocena_pref)
        if pref > 0:
            G.add_edge('Użytkownik', row['nazwa'], weight=pref)
            preferencje[row['nazwa']] = pref

    return G, preferencje

