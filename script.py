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
    url = f"https://api.themoviedb.org/3/search/movie?api_key={tmdb_api_key}&query={tvg_name}"
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
with open("playlist.m3u", "w") as file:
    for row in rows:
        tvg_name = row["tvg-name"]
        
        movie_data = get_movie_data(tvg_name)
        if movie_data:
            logo = f"https://image.tmdb.org/t/p/w600_and_h900_bestv2/{movie_data['poster_path']}" if movie_data['poster_path'] else ""
            description = movie_data["overview"] if movie_data["overview"] else ""
        else:
            logo = ""
            description = ""

        group_title = row["group-title"]
        nome_filme = row["Nome_Filme"]
        
        m3u_line = f'#EXTINF:-1 tvg-type="movie" tvg-name="{tvg_name}" tvg-logo="{logo}" description="{description}" group-title="{group_title}", {nome_filme}\n'
        file.write(m3u_line)
        print(f"Escrevendo linha: {m3u_line.strip()}")

print("Lista M3U gerada com sucesso!")

# Verifique se o arquivo foi criado
if os.path.exists("playlist.m3u"):
    print("Arquivo playlist.m3u criado com sucesso.")
else:
    print("Falha ao criar o arquivo playlist.m3u.")
