import requests
from django.http import JsonResponse
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def peza_api(request):
    # Get user location and category from request
    lat = request.GET.get('lat', '-13.9626')  # Default: Lilongwe
    lon = request.GET.get('lon', '33.7741')
    category = request.GET.get('category', 'all')
    radius = 1000  # 10 km

    # Map service to Overpass API tags
    category_map = {
        'police': 'amenity=police',
        'hospital': 'amenity=hospital',
        'utility': 'office=company',  # For ESCOM/Waterboard
        'ambulance': 'amenity~"hospital|clinic"'  # Include hospitals and clinics
    }

    # Build Overpass query
    query_filter = category_map.get(category, 'amenity=police') if category != 'all' else 'amenity~"police|hospital|clinic|office=company"'
    overpass_query = f"""
        [out:json][timeout:15];
        (
            node[{query_filter}](around:{radius},{lat},{lon});
            way[{query_filter}](around:{radius},{lat},{lon});
        );
        out center;
    """
    url = f"https://overpass-api.de/api/interpreter?data={requests.utils.quote(overpass_query)}"

    try:
        logger.debug(f"Sending Overpass query: {overpass_query}")
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        data = response.json()

        # Parse results
        locations = []
        for element in data.get("elements", []):
            lat = element.get('center', {}).get('lat', element.get('lat'))
            lon = element.get('center', {}).get('lon', element.get('lon'))
            if lat and lon:  # Ensure valid coordinates
                locations.append({
                    "name": element.get("tags", {}).get("name", "Unknown"),
                    "category": element.get("tags", {}).get("amenity", "Unknown"),
                    "address": element.get("tags", {}).get("addr:street", "Unknown Address"),
                    "distance": calculate_distance(float(lat), float(lon), float(request.GET.get('lat', '-13.9626')), float(request.GET.get('lon', '33.7741'))),
                    "lat": lat,
                    "lon": lon
                })

        logger.debug(f"Found {len(locations)} locations")
        return JsonResponse({"locations": locations}, safe=False)

    except requests.RequestException as e:
        logger.error(f"Overpass API error: {str(e)}")
        return JsonResponse({"error": f"Failed to fetch locations: {str(e)}"}, status=500)
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return JsonResponse({"error": f"Server error: {str(e)}"}, status=500)

def calculate_distance(lat1, lon1, lat2, lon2):
    # Simple haversine formula for approximate distance (in km)
    from math import radians, sin, cos, sqrt, atan2
    R = 6371  # Earth's radius in km
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    distance = R * c
    return f"{distance:.1f} km"