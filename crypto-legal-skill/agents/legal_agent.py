def get_regulation(country, topic="stablecoin"):
    mock_data = {
        "Peru": {
            "stablecoin": "Las stablecoins están reguladas por la SBS. Deben registrarse si son usadas como medio de pago.",
            "incorporation": "Las empresas cripto deben registrarse en SUNAT y SBS."
        },
        "US": {
            "stablecoin": "Las stablecoins son consideradas valores por la SEC.",
            "incorporation": "Los DAOs pueden registrarse como LLC en Wyoming o Delaware."
        }
    }
    return mock_data.get(country, {}).get(topic, "Información no disponible.")

if __name__ == "__main__":
    print(get_regulation("Peru", "stablecoin"))