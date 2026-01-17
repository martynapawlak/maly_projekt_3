import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import math

# Funkcje do zadania 2

def calculate_monthly_city_stats(df, cities_list, years_list):
    """
    Oblicza średnie miesięczne.
    """
    # Kopia danych
    df_calc = df.copy()

    # Konwersja indeksu na datetime (jeśli jeszcze nie jest)
    df_calc.index = pd.to_datetime(df_calc.index)

    # Liczymy średnie miesięczne
    monthly_mean = df_calc.resample("ME").mean()

    results = {}

    for city in cities_list:
        # Sprawdzamy kolumny dla miasta (drugi poziom MultiIndexu)
        city_cols = [col for col in monthly_mean.columns if col[1] == city]
        
        if not city_cols:
            print(f"Ostrzeżenie: Brak kolumn dla miasta: {city}")
            continue

        for year in years_list:
            # Wybieramy rok
            data_year = monthly_mean[monthly_mean.index.year == year]
            
            if data_year.empty:
                print(f"Brak danych dla {city} w roku {year}")
                continue

            # Średnia ze wszystkich stacji w mieście
            city_year_mean = data_year[city_cols].mean(axis=1)
            
            # Zamiana indeksu na numer miesiąca (1-12) do wykresu
            city_year_mean.index = city_year_mean.index.month
            
            results[(city, year)] = city_year_mean
            
    return results


def plot_city_comparison(stats_dict):
    """
    Rysuje wykres liniowy dla przygotowanych statystyk.
    """
    plt.figure(figsize=(15, 10))

    # Style wykresów
    styles = {
        ("Katowice", 2015): {"color": "blue", "marker": "o", "linestyle": "--"},
        ("Katowice", 2024): {"color": "green", "marker": "s", "linestyle": "-"},
        ("Warszawa", 2015): {"color": "darkorange", "marker": "o", "linestyle": "--"},
        ("Warszawa", 2024): {"color": "red", "marker": "s", "linestyle": "-"}
    }

    # Sortujemy klucze dla porządku w legendzie
    sorted_keys = sorted(stats_dict.keys())

    if not sorted_keys:
        print("Brak danych do wyrysowania!")
        return

    for key in sorted_keys:
        city, year = key
        data = stats_dict[key]
        
        # Pobieramy styl lub domyślny
        style = styles.get(key, {"color": "gray", "marker": ".", "linestyle": "-"})
        
        plt.plot(data.index, data.values, 
                 label=f"{city} {year}",
                 color=style["color"], 
                 marker=style["marker"], 
                 linestyle=style["linestyle"],
                 linewidth=2, alpha=0.8)

    plt.xticks(range(1, 13), fontsize=12)
    plt.yticks(fontsize=12)
    plt.xlabel('Miesiąc', fontsize=17)
    plt.ylabel('Średnie PM2.5 [µg/m³]', fontsize=17)
    plt.title('Średnie miesięczne stężenie PM2.5 - Porównanie', fontsize=17)
    plt.legend(fontsize=15, title="Miasto i Rok", loc='upper center')
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.show()


# Funkcje do zadania 3.

def prepare_heatmap_data(df, years_list=[2014, 2019, 2024]):
    """
    Przygotowuje dane do heatmapy:
    1. Uśrednia dane ze wszystkich stacji dla każdego miasta.
    2. Filtruje wybrane lata.
    3. Zwraca dane w formacie 'long' (Rok, Miesiąc, Miejscowość, PM2.5).
    """
    # Kopia robocza i konwersja na liczby
    df_calc = df.copy()
    df_calc = df_calc.apply(pd.to_numeric, errors='coerce')
    df_calc.index = pd.to_datetime(df_calc.index)

    # Średnie miesięczne (resample)
    monthly_mean = df_calc.resample("ME").mean()

    # Średnia dla miast (grupowanie po kolumnach)
    # level=1 oznacza drugi poziom MultiIndexu (czyli 'Miejscowość')
    # axis=1 oznacza, że łączymy kolumny, a nie wiersze
    city_means = monthly_mean.groupby(level=1, axis=1).mean()

    # Filtrowanie lat
    mask_years = city_means.index.year.isin(years_list)
    df_filtered = city_means[mask_years]

    # stack() przenosi kolumny (Miasta) do indeksu
    df_long = df_filtered.stack().reset_index()
    
    # Nazywamy kolumny
    # Kolumna 0 to data, 1 to miasto, 2 to wartość 
    df_long.columns = ['Data', 'Miejscowość', 'pm25']
    
    # Wyciągamy Rok i Miesiąc z daty
    df_long['rok'] = df_long['Data'].dt.year
    df_long['miesiac'] = df_long['Data'].dt.month
    
    # Usuwamy pełną datę
    df_return = df_long[['rok', 'miesiac', 'Miejscowość', 'pm25']]
    
    return df_return

def plot_city_heatmaps(df_heatmap):
    """
    Rysuje siatkę heatmap dla każdego miasta.
    Używa wspólnej skali kolorów dla wszystkich wykresów.
    """
    # Lista unikalnych miast
    miejscowosci = df_heatmap['Miejscowość'].unique()
    n_cities = len(miejscowosci)
    
    if n_cities == 0:
        print("Brak danych do wyrysowania (brak miejscowości).")
        return

    # Ustalamy rozmiar siatki
    cols = 3
    rows = math.ceil(n_cities / cols)

    # Ustalamy globalną skalę kolorów (min i max z całych danych)
    # Dzięki temu kolory są porównywalne między miastami
    vmin = df_heatmap['pm25'].min()
    vmax = df_heatmap['pm25'].max()

    fig, axes = plt.subplots(rows, cols, figsize=(cols*5, rows*4), sharex=True, sharey=True)
    
    # Spłaszczamy tablicę osi, żeby łatwo po niej iterować (nawet jak jest 1 wiersz)
    axes_flat = axes.flatten() if n_cities > 1 else [axes]

    for i, ax in enumerate(axes_flat):
        if i < n_cities:
            miasto = miejscowosci[i]
            
            # Filtrujemy dane dla miasta
            df_miasto = df_heatmap[df_heatmap['Miejscowość'] == miasto]
            
            # Pivot table (Rok na osi Y, Miesiąc na osi X)
            pivot = df_miasto.pivot(index='rok', columns='miesiac', values='pm25')
            
            # Rysowanie heatmapy
            # vmin/vmax - kluczowe dla porównywalności
            sns.heatmap(pivot, ax=ax, cmap='coolwarm', vmin=vmin, vmax=vmax, 
                        cbar=True, annot=True, fmt=".1f", linewidths=.5)
            
            ax.set_title(miasto, fontsize=14, fontweight='bold')
            ax.set_xlabel("Miesiąc")
            ax.set_ylabel("Rok")
        else:
            # Ukrywamy puste wykresy (jeśli np. mamy 7 miast a siatkę na 9)
            ax.axis('off')

    plt.suptitle("Średnie miesięczne stężenia PM2.5 [µg/m³]", fontsize=18, y=1)
    plt.tight_layout()
    plt.show()

# Funkcje do zadania 4.

def calculate_daily_exceedances(df, threshold=15):
    """
    Oblicza liczbę dni w roku z przekroczeniem normy dobowej.
    """
    # Kopia i konwersja na liczby
    df_calc = df.copy()
    df_calc = df_calc.apply(pd.to_numeric, errors='coerce')
    
    # Upewniamy się, że indeks to daty
    df_calc.index = pd.to_datetime(df_calc.index)

    # Średnie dobowe (zamiast groupby Rok/Dzień, używamy resample 'D' - Dzień kalendarzowy)
    dobowe = df_calc.resample('D').mean()
    
    # Tworzymy maskę przekroczeń (True/False)
    przekroczenia = (dobowe > threshold)

    # Zliczamy dni (True = 1, False = 0) grupując po Roku
    wynik = przekroczenia.groupby(przekroczenia.index.year).sum()

    return wynik

def plot_manual_bars(wynik, ranking_year, years_to_analyze):
    """
    Rysuje wykres słupkowy używając plt.bar i manualnych przesunięć (x - width itd.),
    """
    
    # Pobieramy rok rankingowy
    if ranking_year not in wynik.index:
        print(f"Brak danych dla roku {ranking_year}")
        return

    rok_rankingowy = wynik.loc[ranking_year]
    
    # Sortujemy malejąco
    rok_sorted = rok_rankingowy.sort_values(ascending=False)
    
    # Zamiana na DataFrame (żeby użyć head/tail tak jak u Ciebie)
    df_sorted = rok_sorted.to_frame(name='wartość')

    # Wybieramy top 3 i bottom 3
    df_najwiecej = df_sorted.head(3)
    df_najmniej = df_sorted.tail(3)

    # Łączymy indeksy
    stacje = df_najwiecej.index.append(df_najmniej.index).unique().tolist()
    
    # Wybieramy tylko wybrane stacje
    df_final = wynik[stacje]
    
    # Wyciągamy nazwy miejscowości (zakładając MultiIndex: Kod, Miasto)
    # Jeśli to zwykły Index, użyje kodów
    if isinstance(df_final.columns, pd.MultiIndex):
        miasta = list(df_final.columns.get_level_values(1))
        # Dodajemy kod stacji do nazwy dla czytelności
        etykiety = [f"{m}\n({k})" for k, m in df_final.columns]
    else:
        miasta = list(df_final.columns)
        etykiety = cities
    
    plt.figure(figsize=(12, 7))
    
    # Konfiguracja osi X
    a = len(stacje)
    x = np.arange(a)
    
    # Szerokość słupka
    width = 0.2
    
    # Rysowanie pętlą po latach (żeby obsłużyć 4 lata: 2015, 2018, 2021, 2024)
    # Obliczamy przesunięcie tak, żeby słupki były wycentrowane wokół X
    # Dla 4 lat przesunięcia to np: -1.5w, -0.5w, +0.5w, +1.5w
    
    liczba_lat = len(years_to_analyze)
    
    for i, year in enumerate(years_to_analyze):
        if year in df_final.index:
            # Obliczenie przesunięcia
            offset = (i - (liczba_lat - 1) / 2) * width
            
            # Pobranie danych dla roku
            wartosci = df_final.loc[year]
            
            # Rysowanie słupka
            plt.bar(x + offset, wartosci, width, label=str(year))

    plt.xticks(x, etykiety, fontsize=10)
    plt.ylabel("Liczba dni z przekroczeniem", fontsize=12)
    plt.title(f"Liczba dni z przekroczeniem normy PM2.5 (>15 µg/m³)\n(Ranking wg roku {ranking_year})", fontsize=14)
    plt.legend(title="Rok")
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    plt.gca().set_axisbelow(True)
    
    plt.tight_layout()
    plt.show()