import os, httpx
from dotenv import load_dotenv
load_dotenv(os.path.expanduser("~/jurisai/.env"))
MAPS_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "")

async def geocodificar_endereco(endereco: str) -> dict:
    if not MAPS_KEY or MAPS_KEY == "AIzaSyAjML1GV9P9WvfCEJmb32RTwjcJDTw1rFA":
        return {"lat": -15.7801, "lng": -47.9292, "endereco_formatado": endereco, "modo": "simulado"}
    async with httpx.AsyncClient() as c:
        r = await c.get("https://maps.googleapis.com/maps/api/geocode/json", params={"address": endereco, "key": MAPS_KEY, "language": "pt-BR"})
        d = r.json()
        if d.get("results"):
            loc = d["results"][0]["geometry"]["location"]
            return {"lat": loc["lat"], "lng": loc["lng"], "endereco_formatado": d["results"][0]["formatted_address"], "modo": "real"}
    return {"erro": "Nao encontrado"}

async def calcular_distancia(origem: str, destino: str) -> dict:
    if not MAPS_KEY or MAPS_KEY == "AIzaSyAjML1GV9P9WvfCEJmb32RTwjcJDTw1rFA":
        return {"distancia": "5.2 km", "duracao": "18 min", "modo": "simulado"}
    async with httpx.AsyncClient() as c:
        r = await c.get("https://maps.googleapis.com/maps/api/distancematrix/json", params={"origins": origem, "destinations": destino, "key": MAPS_KEY, "language": "pt-BR"})
        d = r.json()
        if d.get("rows") and d["rows"][0].get("elements"):
            el = d["rows"][0]["elements"][0]
            if el.get("status") == "OK": return {"distancia": el["distance"]["text"], "duracao": el["duration"]["text"], "modo": "real"}
    return {"erro": "Calculo falhou"}

async def buscar_varas_proximas(cidade: str, tipo: str = "vara civel") -> list:
    if not MAPS_KEY or MAPS_KEY == "AIzaSyAjML1GV9P9WvfCEJmb32RTwjcJDTw1rFA":
        return [{"nome": f"Simulacao: {tipo.title()} de {cidade}", "endereco": "Endereco simulado", "distancia": "2.1 km"}]
    async with httpx.AsyncClient() as c:
        r = await c.get("https://maps.googleapis.com/maps/api/place/textsearch/json", params={"query": f"{tipo} tribunal {cidade} Brasil", "key": MAPS_KEY, "language": "pt-BR"})
        d = r.json()
        return [{"nome": p.get("name"), "endereco": p.get("formatted_address"), "avaliacao": p.get("rating", "N/A")} for p in d.get("results", [])[:5]]
