import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import json
import requests
from googletrans import Translator

# Carregar as credenciais do Google Sheets dos segredos do GitHub Actions
credentials_json = os.environ["GOOGLE_CREDENTIALS_JSON"]
credentials_dict = json.loads(credentials_json)

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)
client = gspread.authorize(credentials)

# Chave de API da TMDb
tmdb_api_key = os.environ["TMDB_API_KEY"]

# Inicializar o tradutor
translator = Translator()

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
m3u_file_path = os.path.join(current_directory, "playlist.m3u")
print(f"Salvando o arquivo M3U em: {m3u_file_path}")
with open(m3u_file_path, "w") as file:
    for row in rows:
        tvg_name = row["tvg-name"]
        
        movie_data = get_movie_data(tvg_name)
        if movie_data:
            logo = f"https://image.tmdb.org/t/p/w600_and_h900_bestv2/{movie_data['poster_path']}" if movie_data['poster_path'] else ""
            description = movie_data["overview"] if movie_data["overview"] else ""
            
            # Traduzir a descrição para o português
            if description:
                translated_description = translator.translate(description, src='en', dest='pt').text
            else:
                translated_description = ""
        else:
            logo = ""
            translated_description = ""

        group_title = row["group-title"]
        nome_filme = row["Nome_Filme"]
        
        m3u_line = f'#EXTINF:-1 tvg-type="movie" tvg-name="{tvg_name}" tvg-logo="{logo}" description="{translated_description}" group-title="{group_title}", {tvg_name}\n'
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
