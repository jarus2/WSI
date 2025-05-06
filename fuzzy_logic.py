import numpy as np
import pandas as pd
import skfuzzy as fuzz

# ===== zakresy =====
cena_range = np.arange(0, 201, 1)
ocena_range = np.arange(0, 5.1, 0.1)
odl_range = np.arange(0, 11, 0.1)

# ===== funkcje przynależności ceny i odległości (trójkątne) =====
tania = fuzz.trimf(cena_range, [0, 0, 60])
srednia = fuzz.trimf(cena_range, [40, 80, 120])
droga = fuzz.trimf(cena_range, [100, 150, 200])

blisko = fuzz.trimf(odl_range, [0, 0, 2.5])
srednio_daleko = fuzz.trimf(odl_range, [1.5, 4, 6])
daleko = fuzz.trimf(odl_range, [5, 8, 10])

# ===== funkcje przynależności oceny (trapezowe) =====
def mu_ocena_niska(x):
    if x <= 2.0:
        return 1
    elif 2.0 < x < 3.5:
        return (3.5 - x) / 1.5
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
    return 0

def mu_ocena_bardzo_dobra(x):
    if x <= 3.5:
        return 0
    elif 3.5 < x < 5.0:
        return (x - 3.5) / 1.5
    return 1

# ===== obliczanie dla danego wiersza przynależności do odpowiednich kryteriów =====
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
