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

# Função para obter dados do filme da TMDb usando o ID
def get_movie_data(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={tmdb_api_key}&language=pt-BR"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()  # Retorna os dados do filme
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
        movie_id = row["id"]  # Usar o campo id da planilha
        
        movie_data = get_movie_data(movie_id)
        if movie_data:
            tvg_name = movie_data["title"]
            logo = f"https://image.tmdb.org/t/p/w600_and_h900_bestv2/{movie_data['poster_path']}" if movie_data['poster_path'] else ""
            description = movie_data["overview"] if movie_data["overview"] else ""
            release_year = movie_data["release_date"].split("-")[0] if "release_date" in movie_data else "N/A"
        else:
            tvg_name = "Unknown"
            logo = ""
            description = ""
            release_year = "N/A"

        group_title = row["group-title"]
        nome_filme = f"{tvg_name} ({release_year})"
        
        m3u_line = f'#EXTINF:-1 tvg-type="movie" tvg-name="{nome_filme}" tvg-logo="{logo}" description="{description}" group-title="{group_title}", {nome_filme}\n\n'
        file.write(m3u_line)
        print(f"Escrevendo linha: {m3u_line.strip()}")

print("Lista M3U gerada com sucesso!")

# Verifique se o arquivo foi criado
if os.path.exists(m3u_file_path):
    print(f"Arquivo {m3u_file_path} criado com sucesso.")
    print("Conteúdo do diretório:")
    for file_name in os.listdir(current_directory):
        print(file_name)
else:
    print(f"Falha ao criar o arquivo {m3u_file_path}.")
