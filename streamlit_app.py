import itertools
import os
import time

import streamlit as st
from geopy.geocoders import Nominatim, GoogleV3
from geopy.distance import geodesic


st.set_page_config(page_title="Otimizador de Rotas", layout="wide")


@st.cache_resource
def get_geolocator():
    """
    Choose geocoder:
    - If GOOGLE_MAPS_API_KEY is configured (Streamlit secrets or env), use Google.
    - Otherwise, fall back to Nominatim.
    """
    api_key = None
    use_google = False

    # 1) Try Streamlit secrets (recommended on Streamlit Cloud)
    try:
        api_key = st.secrets.get("GOOGLE_MAPS_API_KEY", None)
        if api_key:
            use_google = True
    except Exception:
        pass

    # 2) Fallback to environment variable (local .env, etc.)
    if not api_key:
        api_key = os.environ.get("GOOGLE_MAPS_API_KEY")
        if api_key:
            use_google = True

    if api_key and use_google:
        # Google Geocoding – more robust and less likely to be blocked
        return GoogleV3(api_key=api_key, timeout=15), True

    # Default: public Nominatim (can fail/limit on some cloud environments)
    return Nominatim(user_agent="delivery_route_optimizer_streamlit"), False


def geocode_address(address: str, use_google: bool = False):
    """Convert an address to (lat, lon) using Google (if configured) or Nominatim."""
    geolocator, is_google = get_geolocator()
    query = address.strip()
    if not query:
        return None
    
    try:
        if is_google:
            # Google Maps: simpler query
            location = geolocator.geocode(query, exactly_one=True)
        else:
            # Nominatim: try multiple strategies for better results
            location = geolocator.geocode(query, exactly_one=True, timeout=15)
            if not location:
                # Try with Portugal context
                location = geolocator.geocode(f"{query}, Portugal", exactly_one=True, timeout=15)
            if not location:
                # Try without house number
                parts = query.split()
                if len(parts) > 1 and parts[0].isdigit():
                    location = geolocator.geocode(" ".join(parts[1:]), exactly_one=True, timeout=15)
        
        if location:
            return (location.latitude, location.longitude)
        return None
    except Exception as e:
        error_msg = str(e)
        if "Connection refused" in error_msg or "Max retries" in error_msg:
            st.error(f"⚠️ Erro de ligação ao serviço de geocoding. Se estiveres no Streamlit Cloud, configura a Google Maps API Key em Settings → Secrets.")
        else:
            st.warning(f"Geocoding error for {address}: {error_msg}")
        return None


def calculate_distance_time(coord1, coord2):
    """Distance in km and time in minutes (mesma lógica da app Flask)."""
    if not coord1 or not coord2:
        return float("inf"), float("inf")

    distance_km = geodesic(coord1, coord2).kilometers
    time_minutes = (distance_km / 50) * 60 + 5
    return distance_km, time_minutes


def calculate_route_cost(route_coords):
    if len(route_coords) < 2:
        return {"distance": 0, "time": 0, "cost": 0}

    total_distance = 0
    total_time = 0
    for i in range(len(route_coords) - 1):
        dist, t = calculate_distance_time(route_coords[i], route_coords[i + 1])
        total_distance += dist
        total_time += t

    cost = (total_distance * 0.50) + (total_time * 0.20)

    return {
        "distance": round(total_distance, 2),
        "time": round(total_time),
        "cost": round(cost, 2),
    }


def optimize_route(addresses, return_to_start=True):
    """Mesma lógica de otimização mas sem Flask/JSON."""
    if len(addresses) < 2:
        return {"error": "Please provide at least 2 addresses"}

    if len(addresses) > 10:
        return {"error": "Maximum 10 addresses supported for performance reasons"}

    # Check which geocoder is being used
    _, use_google = get_geolocator()
    if use_google:
        st.info("🌍 Usando Google Maps Geocoding API")
    else:
        st.warning("⚠️ Usando OpenStreetMap (Nominatim) - pode ser bloqueado. Configura GOOGLE_MAPS_API_KEY para melhor performance.")
    
    st.write("Geocoding addresses...")
    coords_map = {}
    for addr in addresses:
        coord = geocode_address(addr, use_google)
        if not coord:
            return {"error": f"Could not geocode address: {addr}. Verifica se o endereço está correto ou configura a Google Maps API Key."}
        coords_map[addr] = coord
        if not use_google:
            time.sleep(1)  # rate limit Nominatim (not needed for Google)

    start_address = addresses[0]
    delivery_addresses = addresses[1:]
    if not delivery_addresses:
        return {"error": "Please provide at least one delivery address"}

    num_permutations = len(list(itertools.permutations(delivery_addresses)))
    st.write(f"Analyzing {num_permutations} possible routes...")

    best_route = None
    best_cost = float("inf")

    for perm in itertools.permutations(delivery_addresses):
        if return_to_start:
            route_addresses = [start_address] + list(perm) + [start_address]
        else:
            route_addresses = [start_address] + list(perm)

        route_coords = [coords_map[a] for a in route_addresses]
        route_info = calculate_route_cost(route_coords)

        route_data = {
            "addresses": route_addresses,
            "coordinates": route_coords,
            "distance": route_info["distance"],
            "time": route_info["time"],
            "cost": route_info["cost"],
        }

        if route_info["cost"] < best_cost:
            best_cost = route_info["cost"]
            best_route = route_data

    return {"best_route": best_route}


def format_time(minutes: int) -> str:
    m = round(minutes)
    if m < 60:
        return f"{m} min"
    h = m // 60
    r = m % 60
    if r == 0:
        return f"{h}h"
    return f"{h}h {r} min"


def main():
    st.title("Otimizador de Rotas")
    st.write("Versão Streamlit – partilha este link com os teus amigos depois de deployar. 🚚")

    col1, col2 = st.columns(2)

    with col1:
        start_address = st.text_input("Local de partida (início)", "")
        return_to_start = st.checkbox("Voltar ao local de partida", value=True)

    with col2:
        addresses_text = st.text_area(
            "Endereços de entrega (um por linha)",
            placeholder="Rua Oriental 680 matosinhos\nRua Fresca 318 matosinhos\n...",
        )

    if st.button("Otimizar rota"):
        raw_addresses = [line.strip() for line in addresses_text.splitlines() if line.strip()]

        if not start_address.strip():
            st.error("Por favor indique o local de partida.")
            return

        if not raw_addresses:
            st.error("Por favor introduza pelo menos um endereço de entrega.")
            return

        addresses = [start_address.strip()] + raw_addresses

        with st.spinner("A calcular melhor rota..."):
            result = optimize_route(addresses, return_to_start=return_to_start)

        if "error" in result:
            st.error(result["error"])
            return

        best = result["best_route"]
        st.success("Rota otimizada encontrada!")

        st.subheader("Ordem de paragens")
        for idx, addr in enumerate(best["addresses"]):
            label = "Partida" if idx == 0 else "Chegada" if idx == len(best["addresses"]) - 1 else f"Paragem {idx}"
            st.write(f"**{idx + 1}. {label}:** {addr}")

        st.subheader("Resumo")
        st.write(f"**Distância total:** {best['distance']:.1f} km")
        st.write(f"**Tempo estimado:** {format_time(best['time'])}")
        st.write(f"**Custo estimado:** {best['cost']:.2f} €")


if __name__ == "__main__":
    main()



