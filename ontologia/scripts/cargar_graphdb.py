import argparse
import sys
from pathlib import Path

try:
    import requests
except ImportError:
    print("Falta 'requests'. Instala con: pip install requests")
    sys.exit(2)

BASE = Path(__file__).resolve().parent.parent
ONTO = BASE / "ontologia" / "codefeedback-kg-150.ttl"
SHAPES = BASE / "ontologia" / "shapes-ekg.ttl"

REPO_CONFIG = """@prefix rep: <http://www.openrdf.org/config/repository#> .
@prefix sr: <http://www.openrdf.org/config/repository/sail#> .
@prefix sail: <http://www.openrdf.org/config/sail#> .
@prefix graphdb: <http://www.ontotext.com/config/graphdb#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

[] a rep:Repository ;
   rep:repositoryID "{repo}" ;
   rdfs:label "CodeFeedback-KG" ;
   rep:repositoryImpl [
       rep:repositoryType "graphdb:SailRepository" ;
       sr:sailImpl [
           sail:sailType "graphdb:Sail" ;
           graphdb:ruleset "{ruleset}" ;
           graphdb:base-URL "https://w3id.org/codefeedback-kg/" ;
           graphdb:enable-context-index "true"
       ]
   ] .
"""

VERIFICA = (
    "PREFIX cfkg: <https://w3id.org/codefeedback-kg/schema#> "
    "SELECT (COUNT(DISTINCT ?c) AS ?conceptos) WHERE { ?c a cfkg:Concepto }"
)


def conecta(url):
    try:
        r = requests.get(f"{url}/rest/repositories", timeout=5)
        return r.status_code == 200
    except requests.exceptions.RequestException:
        return False


def repo_existe(url, repo):
    try:
        r = requests.get(f"{url}/rest/repositories", timeout=10)
        r.raise_for_status()
        datos = r.json()
    except requests.exceptions.RequestException as e:
        print(f"Error al consultar los repositorios en {url}: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"Respuesta no valida al listar repositorios en {url}: {e}", file=sys.stderr)
        sys.exit(1)
    return any(x.get("id") == repo for x in datos)


def crea_repo(url, repo, ruleset):
    cfg = REPO_CONFIG.format(repo=repo, ruleset=ruleset)
    files = {"config": ("repo-config.ttl", cfg, "text/turtle")}
    try:
        r = requests.post(f"{url}/rest/repositories", files=files, timeout=30)
    except requests.exceptions.RequestException as e:
        print(f"Error de red al crear el repositorio '{repo}' en {url}: {e}", file=sys.stderr)
        sys.exit(1)
    if r.status_code not in (200, 201):
        raise RuntimeError(f"No se pudo crear el repositorio: {r.status_code} {r.text}")
    print(f"  Repositorio '{repo}' creado (ruleset {ruleset}).")


def carga_ttl(url, repo, ruta, contexto=None):
    endpoint = f"{url}/repositories/{repo}/statements"
    if contexto:
        endpoint += f"?context=%3C{contexto}%3E"
    try:
        data = ruta.read_text(encoding="utf-8").encode("utf-8")
    except OSError as e:
        print(f"Error al leer {ruta}: {e}", file=sys.stderr)
        sys.exit(1)
    try:
        r = requests.post(endpoint, data=data, headers={"Content-Type": "text/turtle"}, timeout=60)
    except requests.exceptions.RequestException as e:
        print(f"Error de red al cargar {ruta.name} en {endpoint}: {e}", file=sys.stderr)
        sys.exit(1)
    if r.status_code not in (200, 204):
        raise RuntimeError(f"Error al cargar {ruta.name}: {r.status_code} {r.text}")
    print(f"  Cargado {ruta.name}" + (f" en <{contexto}>" if contexto else " (grafo por defecto)."))


def consulta(url, repo, q):
    try:
        r = requests.get(
            f"{url}/repositories/{repo}",
            params={"query": q},
            headers={"Accept": "application/sparql-results+json"},
            timeout=30,
        )
        r.raise_for_status()
        datos = r.json()
    except requests.exceptions.RequestException as e:
        print(f"Error de red al ejecutar la consulta de verificacion: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"Respuesta no valida en la consulta de verificacion: {e}", file=sys.stderr)
        sys.exit(1)
    b = datos["results"]["bindings"]
    return b[0]["conceptos"]["value"] if b else "0"


def main():
    ap = argparse.ArgumentParser(description="Carga el CodeFeedback-KG en GraphDB vía REST.")
    ap.add_argument("--url", default="http://localhost:7200")
    ap.add_argument("--repo", default="codefeedback-kg")
    ap.add_argument("--ruleset", default="owl2-rl-optimized")
    ap.add_argument("--shapes", action="store_true", help="Cargar también shapes-ekg.ttl")
    args = ap.parse_args()

    if not conecta(args.url):
        print(f"[X] GraphDB no responde en {args.url}.")
        print("    Arranca GraphDB Desktop y vuelve a ejecutar. Pasos manuales en README-GraphDB.md.")
        sys.exit(1)

    print(f"[OK] Conectado a GraphDB en {args.url}")
    if not repo_existe(args.url, args.repo):
        crea_repo(args.url, args.repo, args.ruleset)
    else:
        print(f"  Repositorio '{args.repo}' ya existe.")

    carga_ttl(args.url, args.repo, ONTO)
    if args.shapes:
        carga_ttl(args.url, args.repo, SHAPES, contexto="http://codefeedback-kg/shapes")

    n = consulta(args.url, args.repo, VERIFICA)
    print(f"[OK] Verificación: {n} conceptos (esperado 157 con inferencia OWL2-RL).")


if __name__ == "__main__":
    main()
