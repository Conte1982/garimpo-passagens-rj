import json
import random
from datetime import datetime, timedelta

# Configuração dos aeroportos do Rio de Janeiro
ORIGINS = ["GIG", "SDU"]

# Destinos monitorados (Nacionais e Internacionais populares)
DESTINATIONS = [
    {"code": "FLN", "name": "Florianópolis", "avg_price": 750},
    {"code": "SSA", "name": "Salvador", "avg_price": 850},
    {"code": "REC", "name": "Recife", "avg_price": 950},
    {"code": "FOR", "name": "Fortaleza", "avg_price": 1100},
    {"code": "EZE", "name": "Buenos Aires", "avg_price": 1800},
    {"code": "SCL", "name": "Santiago", "avg_price": 1600},
    {"code": "MIA", "name": "Miami", "avg_price": 3800},
    {"code": "LIS", "name": "Lisboa", "avg_price": 4500},
]

AIRLINES = ["LATAM", "GOL", "Azul", "Avianca", "JetSMART"]

def scan_flights():
    results = []
    today = datetime.now()

    for origin in ORIGINS:
        for dest in DESTINATIONS:
            # Gera simulação de busca para os próximos 60 dias com permanência de 6 a 10 dias
            for days_ahead in range(10, 60, 5):
                departure = today + timedelta(days=days_ahead)
                for stay in [6, 7, 8, 9, 10]:
                    return_date = departure + timedelta(days=stay)
                    
                    # Simulação de algoritmo de garimpo de preço teto / promoção
                    # Em produção, substitui-se por chamada à API pública do Skyscanner/Google Flights
                    discount_factor = random.uniform(0.55, 0.95)
                    current_price = int(dest["avg_price"] * discount_factor)
                    discount_pct = int(((dest["avg_price"] - current_price) / dest["avg_price"]) * 100)

                    if discount_pct >= 20: # Salva apenas promoções reais (>= 20% OFF)
                        is_direct = random.choice([True, False])
                        airline = random.choice(AIRLINES)
                        
                        booking_url = f"https://www.google.com/travel/flights?q=Flights%20to%20{dest['code']}%20from%20{origin}%20on%20{departure.strftime('%Y-%m-%d')}%20through%20{return_date.strftime('%Y-%m-%d')}"

                        results.append({
                            "origin": origin,
                            "destination_code": dest["code"],
                            "destination_name": dest["name"],
                            "airline": airline,
                            "is_direct": is_direct,
                            "departure_date": departure.strftime("%d/%m/%Y"),
                            "return_date": return_date.strftime("%d/%m/%Y"),
                            "stay_days": stay,
                            "original_price": dest["avg_price"],
                            "promo_price": current_price,
                            "discount_percentage": discount_pct,
                            "booking_url": booking_url
                        })

    # Ordena por maior desconto percentual
    results.sort(key=lambda x: x["discount_percentage"], reverse=True)
    
    # Grava o resultado no JSON lido pelo HTML
    with open("flights.json", "w", encoding="utf-8") as f:
        json.dump(results[:30], f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    scan_flights()
