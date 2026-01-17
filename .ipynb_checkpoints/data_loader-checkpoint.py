import pandas as pd
import requests
import zipfile
import io, os

gios_archive_url = "https://powietrze.gios.gov.pl/pjp/archives/downloadFile/"

# funkcja do ściągania podanego archiwum
def download_gios_archive(year, gios_id, filename):
    # Pobranie archiwum ZIP do pamięci
    url = f"{gios_archive_url}{gios_id}"
    response = requests.get(url)
    response.raise_for_status()  # jeśli błąd HTTP, zatrzymaj

    # Otwórz zip w pamięci
    with zipfile.ZipFile(io.BytesIO(response.content)) as z:
        # znajdź właściwy plik z PM2.5
        if not filename:
            print(f"Błąd: nie znaleziono {filename}.")
            return None
        else:
            # wczytaj plik do pandas
            with z.open(filename) as f:
                try:
                    df = pd.read_excel(f, header=None)
                except Exception as e:
                    print(f"Błąd przy wczytywaniu {year}: {e}")
    return df

# Przykladowe użycie
#df2024 = download_gios_archive(2024, gios_url_ids[2024], gios_pm25_file[2024])

#funkcja do ściągania meta danych - modyfikacja funkcji do ściągania archiwum - bez obsługiwania plików .zip
def download_meta_data(gios_id):
  url = f"{gios_archive_url}{gios_id}"
  response = requests.get(url)
  response.raise_for_status()
  with io.BytesIO(response.content) as f:
    try:
      df_meta = pd.read_excel(f, header=0)
    except  Exception as e:
      print(f"Błąd przy wczytywaniu metadanych: {e}")
  return df_meta
