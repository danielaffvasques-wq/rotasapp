"""
Delivery Route Optimizer - Backend Flask Application
Calculates the most efficient route for 5 delivery addresses.
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import itertools
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import time

app = Flask(__name__)
CORS(app)

# Initialize geocoder (using Nominatim - free, no API key required)
geolocator = Nominatim(user_agent="delivery_route_optimizer")

def geocode_address(address):
    """
    Convert an address to coordinates (latitude, longitude).
    
    Args:
        address: String address
        
    Returns:
        tuple: (latitude, longitude) or None if geocoding fails
    """
    try:
        location = geolocator.geocode(address, timeout=10)
        if location:
            return (location.latitude, location.longitude)
        return None
    except Exception as e:
        print(f"Geocoding error for {address}: {e}")
        return None

def calculate_distance_time(coord1, coord2):
    """
    Calculate distance (km) and estimated time (minutes) between two coordinates.
    Uses straight-line distance and estimates time based on average speed.
    
    Args:
        coord1: (lat, lon) tuple
        coord2: (lat, lon) tuple
        
    Returns:
        tuple: (distance_km, time_minutes)
    """
    if not coord1 or not coord2:
        return (float('inf'), float('inf'))
    
    # Calculate straight-line distance
    distance_km = geodesic(coord1, coord2).kilometers
    
    # Estimate time: assume average speed of 50 km/h in urban areas
    # Add 5 minutes per stop for delivery time
    time_minutes = (distance_km / 50) * 60 + 5
    
    return (distance_km, time_minutes)

def calculate_route_cost(route_coords):
    """
    Calculate total distance, time, and cost for a route.
    
    Args:
        route_coords: List of (lat, lon) tuples representing the route
        
    Returns:
        dict: {'distance': km, 'time': minutes, 'cost': estimated_cost}
    """
    if len(route_coords) < 2:
        return {'distance': 0, 'time': 0, 'cost': 0}
    
    total_distance = 0
    total_time = 0
    
    for i in range(len(route_coords) - 1):
        dist, t = calculate_distance_time(route_coords[i], route_coords[i + 1])
        total_distance += dist
        total_time += t
    
    # Cost calculation: $0.50 per km + $0.20 per minute
    cost = (total_distance * 0.50) + (total_time * 0.20)
    
    return {
        'distance': round(total_distance, 2),
        'time': round(total_time),  # Minutos sempre inteiros, sem casas decimais
        'cost': round(cost, 2)
    }

def optimize_route(addresses, return_to_start=True):
    """
    Find the optimal route by analyzing all possible permutations.
    
    Args:
        addresses: List of address strings (variable length, minimum 2)
        return_to_start: Boolean, whether to return to starting point
        
    Returns:
        dict: Best route information
    """
    if len(addresses) < 2:
        return {'error': 'Please provide at least 2 addresses'}
    
    if len(addresses) > 10:
        return {'error': 'Maximum 10 addresses supported for performance reasons'}
    
    # Geocode all addresses
    print("Geocoding addresses...")
    coords_map = {}
    address_data = []
    for i, addr in enumerate(addresses):
        coord = geocode_address(addr)
        if not coord:
            return {'error': f'Could not geocode address: {addr}'}
        coords_map[addr] = coord
        address_data.append({
            'address': addr,
            'coordinates': coord,
            'index': i
        })
        time.sleep(1)  # Rate limiting for Nominatim (free service)
    
    # Get starting point (first address)
    start_address = addresses[0]
    start_coord = coords_map[start_address]
    
    # Get delivery addresses (remaining addresses)
    delivery_addresses = addresses[1:]
    
    if len(delivery_addresses) == 0:
        return {'error': 'Please provide at least one delivery address'}
    
    # Generate all possible permutations of delivery order
    num_permutations = len(list(itertools.permutations(delivery_addresses)))
    print(f"Analyzing {num_permutations} possible routes...")
    
    best_route = None
    best_cost = float('inf')
    all_routes = []
    
    for perm in itertools.permutations(delivery_addresses):
        # Create full route
        if return_to_start:
            route_addresses = [start_address] + list(perm) + [start_address]
        else:
            route_addresses = [start_address] + list(perm)
        
        route_coords = [coords_map[addr] for addr in route_addresses]
        
        # Calculate route metrics
        route_info = calculate_route_cost(route_coords)
        
        # Store route information with coordinates for map visualization
        route_data = {
            'addresses': route_addresses,
            'coordinates': route_coords,
            'distance': route_info['distance'],
            'time': route_info['time'],
            'cost': route_info['cost'],
            'distance_miles': round(route_info['distance'] * 0.621371, 2)  # Convert km to miles
        }
        all_routes.append(route_data)
        
        # Check if this is the best route (lowest cost)
        if route_info['cost'] < best_cost:
            best_cost = route_info['cost']
            best_route = route_data
    
    # Sort all routes by cost for comparison
    all_routes.sort(key=lambda x: x['cost'])
    
    return {
        'best_route': best_route,
        'all_routes': all_routes[:10],  # Return top 10 routes
        'total_permutations': num_permutations,
        'address_data': address_data
    }

@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')

@app.route('/optimize', methods=['POST'])
def optimize():
    """API endpoint to optimize delivery route."""
    try:
        data = request.json
        addresses = data.get('addresses', [])
        return_to_start = data.get('return_to_start', True)
        
        if len(addresses) < 2:
            return jsonify({'error': 'Please provide at least 2 addresses'}), 400
        
        result = optimize_route(addresses, return_to_start)
        
        if 'error' in result:
            return jsonify(result), 400
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("Starting Delivery Route Optimizer...")
    print("Open http://localhost:5000 in your browser")
    app.run(debug=True, host='0.0.0.0', port=5000)

