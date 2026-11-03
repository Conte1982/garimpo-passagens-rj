import json
from datetime import datetime, timedelta
from fast_flights import FlightQuery, Passengers, create_query

# Aeroportos de Origem no Rio de Janeiro
ORIGINS = ["GIG", "SDU"]

# Lista de destinos nacionais e seus preços médios de referência no mercado (R$)
DESTINATIONS = [
    # --- NORTE ---
    {"code": "MAO", "name": "Manaus (AM)", "avg_price": 1400},
    {"code": "BEL", "name": "Belém (PA)", "avg_price": 1300},
    {"code": "BVB", "name": "Boa Vista (RR)", "avg_price": 1800},

    # --- NORDESTE ---
    {"code": "SLZ", "name": "São Luís (MA)", "avg_price": 1200},
    {"code": "FOR", "name": "Fortaleza (CE)", "avg_price": 1100},
    {"code": "JJD", "name": "Jericoacoara (CE)", "avg_price": 1300},
    {"code": "NAT", "name": "Natal (RN)", "avg_price": 1150},
    {"code": "JPA", "name": "João Pessoa (PB)", "avg_price": 1100},
    {"code": "SSA", "name": "Salvador (BA)", "avg_price": 850},
    {"code": "BPS", "name": "Porto Seguro (BA)", "avg_price": 900},

    # --- SUL ---
    {"code": "CWB", "name": "Curitiba (PR)", "avg_price": 550},
    {"code": "FLN", "name": "Florianópolis (SC)", "avg_price": 750},

    # --- SUDESTE E CENTRO-OESTE ---
    {"code": "CGH", "name": "São Paulo (Congonhas)", "avg_price": 450},
    {"code": "GRU", "name": "São Paulo (Guarulhos)", "avg_price": 450},
    {"code": "VCP", "name": "Campinas (Viracopos)", "avg_price": 500},
    {"code": "BSB", "name": "Brasília (DF)", "avg_price": 600},
]

def scan_real_flights():
    results = []
    today = datetime.now()

    # Varredura na janela ideal de antecedência: entre 30 e 90 dias
    # Passo de 15 dias para manter o tempo de execução ágil no GitHub Actions
    for origin in ORIGINS:
        for dest in DESTINATIONS:
            for days_ahead in range(30, 91, 15):
                departure = today + timedelta(days=days_ahead)
                dep_str = departure.strftime("%Y-%m-%d")
                
                # Testando estadias de 7 e 10 dias (dentro do intervalo de 6 a 10 dias)
                for stay in [7, 10]:
                    return_date = departure + timedelta(days=stay)
                    ret_str = return_date.strftime("%Y-%m-%d")

                    try:
                        # Consulta real no Google Flights
                        query_result = create_query(
                            flights=[
                                FlightQuery(date=dep_str, from_airport=origin, to_airport=dest["code"]),
                                FlightQuery(date=ret_str, from_airport=dest["code"], to_airport=origin)
                            ],
                            trip="round-trip",
                            seat="economy",
                            passengers=Passengers(adults=1)
                        )

                        if query_result and hasattr(query_result, 'flights') and query_result.flights:
                            best_flight = query_result.flights[0]
                            
                            # Tratamento para obter o valor numérico limpo em BRL
                            price_raw = str(getattr(best_flight, 'price', dest["avg_price"]))
                            digits = ''.join(filter(str.isdigit, price_raw))
                            price = int(digits) if digits else dest["avg_price"]

                            discount_pct = int(((dest["avg_price"] - price) / dest["avg_price"]) * 100) if price < dest["avg_price"] else 0
                            
                            booking_url = f"https://www.google.com/travel/flights?q=Flights%20to%20{dest['code']}%20from%20{origin}%20on%20{dep_str}%20through%20{ret_str}"

                            results.append({
                                "origin": origin,
                                "destination_code": dest["code"],
                                "destination_name": dest["name"],
                                "airline": getattr(best_flight, 'name', 'Companhias Variadas'),
                                "is_direct": getattr(best_flight, 'is_direct', True),
                                "departure_date": departure.strftime("%d/%m/%Y"),
                                "return_date": return_date.strftime("%d/%m/%Y"),
                                "stay_days": stay,
                                "original_price": dest["avg_price"],
                                "promo_price": price,
                                "discount_percentage": discount_pct,
                                "booking_url": booking_url
                            })

                    except Exception as e:
                        print(f"Aviso na busca {origin} -> {dest['code']} ({dep_str}): {e}")
                        continue

    # Ordena os resultados pelas ofertas de maior desconto percentual
    results.sort(key=lambda x: x["discount_percentage"], reverse=True)

    # Grava as 40 melhores oportunidades no JSON lido pelo HTML
    with open("flights.json", "w", encoding="utf-8") as f:
        json.dump(results[:40], f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    scan_real_flights()
