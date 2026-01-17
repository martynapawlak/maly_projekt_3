import pandas as pd
import numpy as np

def delete_rows(year, data_frame, tab_of_indexes):
    for i in tab_of_indexes:
        try:
            data_frame.drop(i, inplace=True)
            print(f"W tabeli {year} usunięto wiersz {i}")
        except:
            print(f"W tabeli {year} nie ma wiersza {i}, zatem pomijam usuwanie.")
    return data_frame


def normalize_dataframe(df):
    """
    Zamienia przecinki na kropki w całym DataFrame, próbuje konwertować na liczby.
    Zwraca wyczyszczony DataFrame oraz liczbę zmienionych komórek.
    """
    # Kopia oryginału do porównania i uzupełniania miejsc, 
    # gdzie konwersja się nie udała (np. tekst)
    df_old = df.copy()

    # Zamiana przecinków na kropki (globalnie w stringach)
    # regex=True pozwala znaleźć przecinki wewnątrz tekstów
    df_temp = df.replace(',', '.', regex=True)

    # Próba konwersji na liczby (cały DF naraz)
    # errors='coerce' zamienia błędy (teksty) na NaN
    df_numeric = df_temp.apply(pd.to_numeric, errors='coerce')

    # Złożenie wyniku:
    # Tam gdzie mamy liczbę (sukces konwersji) -> bierzemy z df_numeric
    # Tam gdzie jest NaN (bo był tekst) -> przywracamy wartość z df_old
    df_cleaned = df_numeric.fillna(df_old)

    # Liczenie zmian
    # Rzutowanie na str jest bezpieczne dla porównań (omija problem NaN != NaN)
    changes_count = (df_cleaned.astype(str) != df_old.astype(str)).sum().sum()

    return df_cleaned, changes_count

import pandas as pd

import pandas as pd

def unify_station_codes(data_dict, df_meta):
    """
    Podmienia stare kody stacji na nowe w nagłówkach kolumn.
    Obsługuje sytuację, gdy 'Kod stacji' jest indeksem w df_meta.
    """
    
    # Robimy kopię i resetujemy indeks, aby 'Kod stacji' stał się zwykłą kolumną.
    # Dzięki temu mamy dostęp zarówno do 'Stary Kod...' jak i 'Kod stacji'.
    df_meta_temp = df_meta.reset_index()
    
    # Upewnij się, że nazwa kolumny ze starym kodem jest identyczna jak w Excelu
    # (często zawiera znaki nowej linii \n)
    col_old = 'Stary Kod stacji \n(o ile inny od aktualnego)'
    col_new = 'Kod stacji'
    
    # Zabezpieczenie: Sprawdźmy czy kolumny istnieją po reset_index
    if col_new not in df_meta_temp.columns:
        # Jeśli indeks nie miał nazwy, reset_index nazwie go 'index'. 
        # Próbujemy to naprawić, jeśli nazwa była inna.
        if df_meta.index.name:
            col_new = df_meta.index.name
        else:
            # Fallback jeśli indeks nie ma nazwy
            col_new = df_meta_temp.columns[0] 

    mapowanie = {}
    
    # Pobieramy tylko interesujące nas kolumny i usuwamy puste (tam gdzie nie ma starego kodu)
    try:
        subset = df_meta_temp[[col_old, col_new]].dropna()
    except KeyError as e:
        print(f"Błąd: Nie znaleziono kolumn w metadanych. Dostępne kolumny to: {df_meta_temp.columns.tolist()}")
        raise e

    for _, row in subset.iterrows():
        old_val = row[col_old]
        new_val = row[col_new]
        
        # Obsługa wielu kodów po przecinku
        for part in str(old_val).split(','):
            clean_old = part.strip()
            if clean_old != new_val:
                mapowanie[clean_old] = new_val

    for year, df in data_dict.items():
        iteration = 0
        while True:
            iteration += 1
            current_cols = df.columns.tolist()
            
            # Mapowanie nazw kolumn
            new_cols = [mapowanie.get(col, col) for col in current_cols]
            
            if new_cols == current_cols:
                break
            
            # Liczymy zmiany
            changed_count = sum(1 for old, new in zip(current_cols, new_cols) if old != new)
            
            # Aplikujemy zmiany
            df.columns = new_cols
            
            # (Opcjonalnie) Wypisujemy info tylko, jeśli coś się zmieniło
            if changed_count > 0:
                print(f"[{year}] Iteracja {iteration}: zaktualizowano {changed_count} kodów stacji.")

    return data_dict

def filter_common_stations(data_dict):
    """
    Pozostawia w DataFrame'ach tylko te kolumny (stacje), które występują
    we wszystkich latach (kluczach słownika).
    
    Argumenty:
    data_dict -- słownik {rok: dataframe}
    
    Zwraca:
    Zmodyfikowany słownik data_dict z przefiltrowanymi kolumnami.
    """
    
    # Zabezpieczenie przed pustym słownikiem
    if not data_dict:
        print("Słownik danych jest pusty.")
        return data_dict

    # Znalezienie wspólnych kolumn 
    # Pobieramy kolumny z pierwszego dostępnego roku jako punkt startowy
    first_key = next(iter(data_dict))
    common_cols = set(data_dict[first_key].columns)

    # Przecięcie zbiorów kolumn ze wszystkich lat
    for df in data_dict.values():
        common_cols &= set(df.columns)

    # Sortujemy, aby kolejność kolumn była identyczna w każdym DataFrame
    # (set nie gwarantuje kolejności, a sorted list tak)
    sorted_common_cols = sorted(list(common_cols))
    
    print(f"Znaleziono {len(sorted_common_cols)} wspólnych stacji dla wszystkich lat.\n")

    # Filtrowanie danych
    for year, df in data_dict.items():
        cols_before = df.shape[1]
        
        # Nadpisujemy DataFrame tylko wybranymi kolumnami
        data_dict[year] = df[sorted_common_cols]
        
        cols_after = data_dict[year].shape[1]
        removed = cols_before - cols_after
        
        print(f"Rok {year}: usunięto {removed} stacji (pozostało {cols_after}).")
        
    return data_dict

import pandas as pd

def add_city_to_columns(data_dict, df_meta):
    """
    Dodaje drugi poziom nagłówków (MultiIndex) do kolumn: (Kod stacji, Miejscowość).
    
    Argumenty:
    data_dict -- słownik {rok: dataframe}, gdzie kolumny to kody stacji
    df_meta   -- dataframe z metadanymi
    
    Zwraca:
    Zmodyfikowany słownik data_dict z MultiIndex na kolumnach.
    """
    
    # Przygotowanie mapy Kod -> Miasto
    # Resetujemy indeks w meta, żeby mieć pewność, że 'Kod stacji' jest dostępny jako kolumna
    df_meta_temp = df_meta.reset_index()
    
    # Sprawdzenie nazwy kolumny z kodem (zabezpieczenie)
    col_code = 'Kod stacji'
    if col_code not in df_meta_temp.columns and df_meta.index.name == col_code:
        # Jeśli nie znaleziono kolumny, ale indeks tak się nazywa - to po resecie będzie miał starą nazwę
        pass 
    elif col_code not in df_meta_temp.columns:
        # Fallback - szukamy pierwszej kolumny, która wygląda na kod, lub zgłaszamy błąd
        # Zakładamy, że po resecie indeksu, stara nazwa indeksu może być 'index' lub inna
        pass 

    # Tworzymy słownik mapujący: 'DsWroc...' -> 'Wrocław'
    try:
        # dropna() usuwa stacje, które nie mają przypisanego miasta
        station_city_map = df_meta_temp.set_index('Kod stacji')['Miejscowość'].dropna().to_dict()
    except KeyError:
        print("Błąd: Nie znaleziono kolumny 'Kod stacji' lub 'Miejscowość' w metadanych.")
        return data_dict

    # Aktualizacja DataFrame'ów 
    for year, df in data_dict.items():
        # Pobieramy obecne nagłówki (kody stacji)
        current_codes = df.columns.tolist()
        
        # Dla każdego kodu szukamy miasta w słowniku.
        # Jeśli nie znajdzie, wpisuje 'Nieznane' (lub pusty string '', jak wolałeś)
        cities = [station_city_map.get(code, 'Nieznane') for code in current_codes]
        
        # Tworzymy pary (Kod, Miasto)
        multi_columns = list(zip(current_codes, cities))
        
        # Tworzymy MultiIndex
        new_index = pd.MultiIndex.from_tuples(multi_columns, names=['Kod stacji', 'Miejscowość'])
        
        # Przypisujemy nowy indeks do kolumn
        df.columns = new_index
        
        # Diagnostyka
        matched_count = sum(1 for city in cities if city != 'Nieznane')
        print(f"Rok {year}: przypisano miasto do {matched_count}/{len(current_codes)} stacji.")

    return data_dict

import pandas as pd

def combine_dataframes(data_dict):
    """
    Łączy słownik DataFrame'ów (podzielonych latami) w jeden długi DataFrame.
    Zachowuje indeks (Datę/Czas) i sortuje chronologicznie.
    
    Argumenty:
    data_dict -- słownik {rok: dataframe}
    
    Zwraca:
    Jeden połączony DataFrame.
    """
    if not data_dict:
        print("Brak danych do połączenia.")
        return None

    # Pobieramy listę DataFrame'ów posortowaną po kluczach (latach), 
    # żeby łączyć w dobrej kolejności (2014 -> 2018 -> 2024)
    sorted_dfs = [data_dict[year] for year in sorted(data_dict.keys())]

    # Łączenie (konkatenacja)
    # axis=0 -> łączymy wiersze (jeden pod drugim)
    # ignore_index=False -> ZACHOWUJEMY daty w indeksie!
    combined_df = pd.concat(sorted_dfs, axis=0, ignore_index=False)
    
    # Dla pewności sortujemy po indeksie (czasie), 
    # na wypadek gdyby lata w słowniku były niepo kolei
    combined_df = combined_df.sort_index()

    print(f"Połączono {len(data_dict)} roczników.")
    print(f"Wynikowy rozmiar: {combined_df.shape}")
    
    return combined_df

def fix_midnight_dates(df):
    """
    Korekta dat dla godziny 00:00:00 (tzw. "godzina 24:00").
    Zmienia 00:00:00 na 23:59:59 dnia poprzedniego.
    Następnie usuwa czas, zostawiając samą datę w indeksie.
    
    Argumenty:
    df -- DataFrame z indeksem typu Datetime (lub kolumną daty)
    
    Zwraca:
    DataFrame z poprawionym indeksem (tylko daty).
    """
    # Upewniamy się, że pracujemy na kopii
    df = df.copy()
    
    # Sprawdzamy, czy indeks to daty. Jeśli nie, próbujemy przekonwertować.
    # (W Twoim przypadku po combine_dataframes indeks powinien być już datetime)
    if not isinstance(df.index, pd.DatetimeIndex):
        print("Indeks nie jest typu datetime. Próbuję konwersji...")
        df.index = pd.to_datetime(df.index)

    # Logika przesunięcia o 1 sekundę
    # Pobieramy indeks jako Serię, żeby móc użyć .where
    dates = df.index.to_series()
    
    # JEŚLI godzina != 0 -> Zostaw bez zmian
    # W PRZECIWNYM RAZIE (godzina 00:00) -> Odejmij 1 sekundę
    # Efekt: 2024-01-02 00:00:00 zamieni się na 2024-01-01 23:59:59
    new_dates = dates.where(
        dates.dt.hour != 0, 
        dates - pd.Timedelta(seconds=1)
    )
    
    # Usunięcie czasu (rzutowanie na date)
    # Teraz 2024-01-01 23:59:59 stanie się po prostu 2024-01-01
    df.index = new_dates.dt.date
    
    # Nadajemy nazwę indeksowi
    df.index.name = 'Data'
    
    return df