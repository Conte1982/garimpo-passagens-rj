import json
import re
from datetime import datetime, timedelta
from playwright.sync_api import sync_playwright

ORIGINS = ["GIG", "SDU"]

# Seleção dos principais destinos nacionais (foco em execuções rápidas e precisas)
DESTINATIONS = [
    {"code": "FOR", "name": "Fortaleza (CE)", "avg_price": 1100},
    {"code": "SSA", "name": "Salvador (BA)", "avg_price": 850},
    {"code": "REC", "name": "Recife (PE)", "avg_price": 950},
    {"code": "NAT", "name": "Natal (RN)", "avg_price": 1150},
    {"code": "MAO", "name": "Manaus (AM)", "avg_price": 1400},
    {"code": "FLN", "name": "Florianópolis (SC)", "avg_price": 750},
    {"code": "CWB", "name": "Curitiba (PR)", "avg_price": 550},
    {"code": "CGH", "name": "São Paulo (Congonhas)", "avg_price": 450},
    {"code": "BSB", "name": "Brasília (DF)", "avg_price": 600},
    {"code": "SLZ", "name": "São Luís (MA)", "avg_price": 1200},
]

def scan_real_flights_playwright():
    results = []
    today = datetime.now()

    with sync_playwright() as p:
        # Lança o navegador Chromium em modo invisível
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            locale="pt-BR"
        )
        page = context.new_page()

        # Janela estratégica de antecedência: 45 e 60 dias (estadia de 7 dias)
        for days_ahead in [45, 60]:
            departure = today + timedelta(days=days_ahead)
            dep_str = departure.strftime("%Y-%m-%d")
            return_date = departure + timedelta(days=7)
            ret_str = return_date.strftime("%Y-%m-%d")

            for origin in ORIGINS:
                for dest in DESTINATIONS:
                    booking_url = f"https://www.google.com/travel/flights?q=Flights%20to%20{dest['code']}%20from%20{origin}%20on%20{dep_str}%20through%20{ret_str}"

                    try:
                        # Navega até o Google Flights
                        page.goto(booking_url, timeout=30000, wait_until="domcontentloaded")
                        page.wait_for_timeout(3000) # Aguarda renderização dos preços

                        content = page.content()
                        
                        # Captura valores numéricos no formato de Reais (R$)
                        matches = re.findall(r'R\$\s?(\d{1,3}(?:\.\d{3})?)', content)
                        
                        if matches:
                            clean_prices = [int(m.replace('.', '')) for m in matches if int(m.replace('.', '')) > 150]
                            if clean_prices:
                                real_price = min(clean_prices)
                                original_avg = dest["avg_price"]
                                discount_pct = int(((original_avg - real_price) / original_avg) * 100) if real_price < original_avg else 0

                                results.append({
                                    "origin": origin,
                                    "destination_code": dest["code"],
                                    "destination_name": dest["name"],
                                    "airline": "Google Flights (Ao Vivo)",
                                    "is_direct": True,
                                    "departure_date": departure.strftime("%d/%m/%Y"),
                                    "return_date": return_date.strftime("%d/%m/%Y"),
                                    "stay_days": 7,
                                    "original_price": original_avg,
                                    "promo_price": real_price,
                                    "discount_percentage": discount_pct,
                                    "booking_url": booking_url
                                })
                                print(f"Capturado com sucesso: {origin} -> {dest['code']} = R$ {real_price}")
                    except Exception as e:
                        print(f"Erro em {origin} -> {dest['code']}: {e}")
                        continue

        browser.close()

    # Ordena pelos preços reais capturados (do menor para o maior)
    results.sort(key=lambda x: x["promo_price"])

    with open("flights.json", "w", encoding="utf-8") as f:
        json.dump(results[:30], f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    scan_real_flights_playwright()
