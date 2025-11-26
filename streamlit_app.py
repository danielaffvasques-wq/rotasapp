import itertools
import time

import streamlit as st
from geopy.geocoders import Nominatim
from geopy.distance import geodesic


st.set_page_config(page_title="Otimizador de Rotas", layout="wide")


@st.cache_resource
def get_geolocator():
    # Simple Nominatim geocoder (sem Google)
    return Nominatim(user_agent="delivery_route_optimizer_streamlit")


def geocode_address(address: str):
    """Convert an address to (lat, lon) using Nominatim."""
    geolocator = get_geolocator()
    query = address.strip()
    if not query:
        return None
    try:
        location = geolocator.geocode(query, timeout=15, exactly_one=True)
        if location:
            return (location.latitude, location.longitude)
        return None
    except Exception as e:
        st.write(f"Geocoding error for {address}: {e}")
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

    st.write("Geocoding addresses...")
    coords_map = {}
    for addr in addresses:
        coord = geocode_address(addr)
        if not coord:
            return {"error": f"Could not geocode address: {addr}"}
        coords_map[addr] = coord
        time.sleep(1)  # rate limit Nominatim

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



