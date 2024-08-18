import requests
from dotenv import load_dotenv
import os
from dateutil import parser
from datetime import datetime, timezone


load_dotenv('.env')

GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')

QUERY = """
query ($after: String) {
  search(query: "stars:>1", type: REPOSITORY, first: 20, after: $after) {
    edges {
      node {
        ... on Repository {
          nameWithOwner
          createdAt
          pullRequests(states: MERGED) {
            totalCount
          }
          releases {
            totalCount
          }
          updatedAt
          primaryLanguage {
            name
          }
          issues {
            totalCount
          }
          closed: issues(states: CLOSED) {
            totalCount
          }
          stargazers {
            totalCount
          }
        }
      }
      cursor
    }
    pageInfo {
      endCursor
      hasNextPage
    }
  }
}
"""

def format_date(iso_date, date_format="%d/%m/%Y %H:%M:%S"):
    date = parser.isoparse(iso_date)
    
    return date.strftime(date_format)

# Função para calcular o tempo em dia entre a data atual e a data recebida
def calculate_time_between_dates_in_days(iso_date):
    creation_date = parser.isoparse(iso_date)
    now = datetime.now(timezone.utc)
    age = (now - creation_date).days
    return age

# Calcula a razão entre o número de issues fechadas e o total de issues
def issues_resolution_percentage(closed_issues, total_issues):
    if total_issues == 0:
        return 0
    percentage = (closed_issues / total_issues) * 100
    return round(percentage, 2)

def fazer_requisicao(url, headers, payload):
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Erro na solicitação: {e}")
        return None

def coletar_dados_repositorios(token, query, variaveis=None):
    url = 'https://api.github.com/graphql'
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    payload = {'query': query, 'variables': variaveis}
    return fazer_requisicao(url, headers, payload)

def exibir_dados_repositorios(dados):

  
    for repo in dados:
        print(f"Nome do Repositório: {repo['nameWithOwner']}")
        print(f"Data de Criação: {repo['createdAt']}")
        print(f"Total de Pull Requests: {repo['pullRequests']['totalCount']}")
        print(f"Total de Releases: {repo['releases']['totalCount']}")
        print(f"Última Atualização: {repo['updatedAt']}")
        linguagem = repo['primaryLanguage']['name'] if repo.get('primaryLanguage') else 'Desconhecida'
        print(f"Linguagem Primária: {linguagem}")
        print(f"Total de Issues: {repo['issues']['totalCount']}")
        print(f"Total de Issues Fechadas: {repo['closed']['totalCount']}")
        print(f"Total de Estrelas: {repo['stargazers']['totalCount']}")
        print('-' * 40)

def main():
    quantidade_desejada = 100
    variaveis = {'after': None}
    dados = []
    
    while len(dados) < quantidade_desejada:
        resultado = coletar_dados_repositorios(GITHUB_TOKEN, QUERY, variaveis)
        if not resultado:
            break
        
        repositorios = resultado.get('data', {}).get('search', {}).get('edges', [])
        if not repositorios:
            break
        
        dados.extend(repo['node'] for repo in repositorios)
        
        page_info = resultado.get('data', {}).get('search', {}).get('pageInfo', {})
        if not page_info.get('hasNextPage', False):
            break
        
        variaveis['after'] = page_info.get('endCursor', None)
    
    exibir_dados_repositorios(dados[:quantidade_desejada])

if __name__ == '__main__':
    main()
