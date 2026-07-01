import requests
import time
import webbrowser
import os

# Repositorios a monitorizar (SOLO LOS QUE SÍ EXISTEN)
REPOS = [
    "xevrion-v2/agent-playground",
    "UnsafeLabs/Bounty-Hunters",
    "moorcheh-ai/memanto",
    "livepeer/explorer"
]

# Limpiar pantalla
def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def check_bounties():
    for repo in REPOS:
        url = f"https://api.github.com/repos/{repo}/issues"
        params = {
            "state": "open",
            "labels": "bounty",
            "sort": "created",
            "direction": "desc",
            "per_page": 5
        }
        try:
            response = requests.get(url, params=params)
            if response.status_code != 200:
                continue
            issues = response.json()
            for issue in issues:
                comments = issue.get("comments", 0)
                # Si tiene menos de 3 comentarios y no tiene PRs abiertas
                if comments < 3:
                    print(f"🔔 {repo}")
                    print(f"   Título: {issue['title']}")
                    print(f"   Enlace: {issue['html_url']}")
                    print(f"   Comentarios: {comments}")
                    print(f"   ¡RECLÁMALO AHORA!")
                    print("-" * 50)
                    # Abrir en navegador
                    webbrowser.open(issue['html_url'])
        except Exception as e:
            print(f"Error en {repo}: {e}")

if __name__ == "__main__":
    clear()
    print("=" * 50)
    print("  🦁 MONITOR DE BOUNTIES GITHUB")
    print("=" * 50)
    print(f"Repositorios monitorizados: {len(REPOS)}")
    print("Cada 60 segundos se buscarán nuevos bounties.")
    print("Presiona Ctrl+C para detener.")
    print("=" * 50)
    
    while True:
        print(f"\n🔍 Buscando bounties nuevos... ({time.ctime()})")
        check_bounties()
        print(f"⏳ Esperando 60 segundos...")
        time.sleep(60)
        clear()