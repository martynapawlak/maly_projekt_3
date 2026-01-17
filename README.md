# Analiza danych PM2.5 w Polsce

Projekt analizuje dane PM2.5 z różnych stacji pomiarowych w Polsce. Oblicza średnie miesięczne, dobowe stężenia oraz generuje wykresy porównawcze dla miast i lat. Identyfikuje również dni z przekroczeniem normy.

## Struktura projektu

projekt3/
|-- .ipynb_checkpoints
| |-- data_loader-checkpoint.py
| |-- projekt_1_Martyna_Pawlak_Szymon_Debowski-checkpoint.ipynb
|-- src
| |-- __init__.py
|-- tests/ # testy jednostkowe dla modułów
| |-- test_data_cleaner.py
| |-- test_data_statistics.py
|-- .gitignore
|-- data_cleaner.py # funkcje do czyszczenia i przetwarzania danych
|-- data_loader.py # funkcje do pobierania danych i metadanych z GIOŚ
|-- data_statistics.py # funkcje obliczające statystyki i wykresy
|-- README.md # dokumentacja projektu
|-- projekt_1_Martyna_Pawlak_Szymon_Debowski.ipynb
|-- projekt_3.ipynb

---

## Wymagania pakietów
- python >= 3.11
- pandas
- numpy
- seaborn
- matplotlib
- pytest

Wszystkie pakiety zainstalujesz poleceniem:
```bash
pip install pandas numpy seaborn matplotlib pytest
```


## Instalacja
1. Sklonuj repozytorium
``` bash
git clone https://github.com/martynapawlak/maly_projekt_3.git 
```

2. Opcjonalnie stwórz wirtualne środowisko

3. Zainstaluj wymagane pakiety


## Uruchomienie testów
```bash
PYTHONPATH=. pytest
```

## Przykład użycia
W notatniku projekt_3.ipynb znajdziesz przykłady 

## Autorzy
Martyna Pawlak, Szymon Dębowski




