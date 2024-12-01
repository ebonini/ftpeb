import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import json
import requests

# Carregar as credenciais do Google Sheets dos segredos do GitHub Actions
credentials_json = os.environ["GOOGLE_CREDENTIALS_JSON"]
credentials_dict = json.loads(credentials_json)

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)
client = gspread.authorize(credentials)

# Chave de API da TMDb
tmdb_api_key = os.environ["TMDB_API_KEY"]

# Função para obter dados do filme da TMDb
def get_movie_data(tvg_name):
    url = f"https://api.themoviedb.org/3/search/movie?api_key={tmdb_api_key}&query={tvg_name}&language=pt-BR"
    response = requests.get(url)
    if response.status_code == 200:
        results = response.json().get("results")
        if results:
            return results[0]  # Retorna o primeiro resultado
    return None

# Verificar o diretório de trabalho atual
current_directory = os.getcwd()
print(f"Diretório de trabalho atual: {current_directory}")

# Abrir a planilha
spreadsheet = client.open("BASE")
worksheet = spreadsheet.sheet1

# Pegar todas as linhas da planilha
rows = worksheet.get_all_records()

# Gerar a lista M3U
m3u_file_path = os.path.join(current_directory, "playlist.m3u")
print(f"Salvando o arquivo M3U em: {m3u_file_path}")
with open(m3u_file_path, "w") as file:
    for row in rows:
        tvg_name = row["tvg-name"]
        
        movie_data = get_movie_data(tvg_name)
        if movie_data:
            logo = f"https://image.tmdb.org/t/p/w600_and_h900_bestv2
