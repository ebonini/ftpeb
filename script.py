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

# Verificar se a autenticação foi bem-sucedida
try:
    spreadsheet = client.open("BASE")
    print("Autenticação bem-sucedida e acesso à planilha garantido.")
except gspread.exceptions.SpreadsheetNotFound:
    print("Planilha não encontrada. Verifique o nome e as permissões.")
    raise
except Exception as e:
    print(f"Erro na autenticação ou acesso: {e}")
    raise

# Pegar a primeira worksheet da planilha
worksheet = spreadsheet.sheet1

# Pegar todas as linhas da planilha
rows = worksheet.get_all_records()

# Gerar a lista M3U
with open("playlist.m3u", "w") as file:
    for row in rows:
        tvg_name = row["tvg-name"]
        
        # Adicione aqui a lógica para obter os dados da TMDb
        
        m3u_line = f'#EXTINF:-1 tvg-type="movie" tvg-name="{tvg_name}" tvg-logo="{logo}" description="{description}" group-title="{group_title}", {nome_filme}\n'
        file.write(m3u_line)

print("Lista M3U gerada com sucesso!")
