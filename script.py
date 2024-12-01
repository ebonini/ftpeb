import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import json

# Carregar as credenciais do Google Sheets dos segredos do GitHub Actions
credentials_json = os.environ["GOOGLE_CREDENTIALS_JSON"]
credentials_dict = json.loads(credentials_json)

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)
client = gspread.authorize(credentials)

# Abrir a planilha
spreadsheet = client.open("Nome_da_Sua_Planilha")
worksheet = spreadsheet.sheet1

# Pegar todas as linhas da planilha
rows = worksheet.get_all_records()

# Gerar a lista M3U
with open("playlist.m3u", "w") as file:
    for row in rows:
        tvg_name = row["tvg-name"]
        logo = row["tvg-logo"]
        description = row["description"]
        group_title = row["group-title"]
        nome_filme = row["Nome_Filme"]
        
        m3u_line = f'#EXTINF:-1 tvg-type="movie" tvg-name="{tvg_name}" tvg-logo="{logo}" description="{description}" group-title="{group_title}", {nome_filme}\n'
        file.write(m3u_line)

print("Lista M3U gerada com sucesso!")
