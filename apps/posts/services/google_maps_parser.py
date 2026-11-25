import json
import logging
import os
import re
import urllib.parse
from typing import Any, Dict, List, Optional, Tuple

import requests
from django.conf import settings
from django.core.files.base import ContentFile
from django.db.models import Q

from apps.posts.models import Category, Post, PostImage, PostSocialMedia, PostWorkDays
from apps.shared.models import District, Region

logger = logging.getLogger(__name__)

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "uz,ru;q=0.9,en-US;q=0.8,en;q=0.7",
}

CATEGORY_KEYWORDS: Dict[str, List[str]] = {
    "Football": ["football", "futbol", "стадион", "stadium", "soccer", "maydon", "футбол"],
    "Volleyball": ["volleyball", "voleybol", "волейбол"],
    "PlayStation": ["playstation", "ps4", "ps5", "game club", "gaming club", "sony"],
    "PC Gaming": ["pc gaming", "kompyuter", "cyber", "kompyuter klubi", "киберклуб", "internet cafe"],
    "Fitness": ["fitness", "fitnes", "gym", "sport zal", "trenajor", "тренажерный", "фитнес", "crossfit"],
    "Table Tennis": ["table tennis", "stol tennisi", "настольный теннис", "ping pong"],
    "Tennis": ["tennis", "kort", "корт", "теннис"],
    "Swimming pool": ["swimming", "suzish", "basseyn", "бассейн", "pool", "akvapark", "аквапарк"],
    "Phone Repair": ["telefon ta'mirlash", "phone repair", "remont telefonov", "servis telefon", "ремонт телефонов"],
    "Yoga": ["yoga", "йога", "pilates", "пилатес"],
    "Watch Repair": ["soat ta'mirlash", "watch repair", "ремонт часов"],
    "Barbershop": ["barbershop", "barber", "sartaroshxona", "барбершоп", "мужская стрижка"],
    "Women's Beauty Salon": ["beauty salon", "go'zallik saloni", "салон красоты", "spa", "маникюр", "lash"],
    "Shoe Repair": ["shoe repair", "oyoq kiyim ta'mirlash", "ремонт обуви"],
    "Tailoring": ["tailoring", "kiyim tikish", "atelie", "ателье"],
    "Karaoke": ["karaoke", "караоке"],
    "Ice Skating": ["ice skating", "konki", "muz saroyi", "каток", "ледовый"],
    "Equestrian Sports": ["equestrian", "ot sporti", "ippodrom", "ипподром", "horse"],
    "Dry Cleaning": ["dry cleaning", "ximchistka", "химчистка", "kir yuvish"],
    "Car Services": ["car service", "avtoservis", "moyka", "автосервис", "avtomobil", "detailing"],
    "Bowling": ["bowling", "bouling", "боулинг"],
    "Billiards": ["billiards", "bilyard", "бильярд"],
    "Children's Playground": ["playground", "bolalar", "детская площадка", "kids park"],
    "Basketball": ["basketball", "basketbol", "баскетбол"],
    "Chess": ["chess", "shaxmat", "шахматы"],
    "Karting": ["karting", "картинг"],
    "Bicycle Riding": ["bicycle", "velosiped", "велосипед", "velo"],
    "Golf": ["golf", "гольф"],
}


class GoogleMapsParserService:
    def __init__(self, google_api_key: Optional[str] = None):
        self.api_key = (
            google_api_key
            or getattr(settings, "GOOGLE_MAPS_API_KEY", None)
            or getattr(settings, "GOOGLE_PLACES_API_KEY", None)
            or os.getenv("GOOGLE_MAPS_API_KEY")
            or os.getenv("GOOGLE_PLACES_API_KEY")
        )

    def resolve_url(self, url: str) -> str:
        """Resolve short links (maps.app.goo.gl, goo.gl/maps) to final canonical URL."""
        if not url:
            return ""
        clean_url = url.strip()
        if not clean_url.startswith("http://") and not clean_url.startswith("https://"):
            clean_url = "https://" + clean_url

        try:
            resp = requests.head(
                clean_url,
                headers=DEFAULT_HEADERS,
                allow_redirects=True,
                timeout=12,
            )
            return resp.url
        except Exception as e:
            logger.warning(f"Failed to resolve head for {clean_url}: {e}")
            try:
                resp = requests.get(
                    clean_url,
                    headers=DEFAULT_HEADERS,
                    allow_redirects=True,
                    timeout=12,
                )
                return resp.url
            except Exception as e2:
                logger.error(f"Failed to resolve url {clean_url}: {e2}")
                return clean_url

    def extract_coordinates_from_url(self, url: str) -> Tuple[Optional[float], Optional[float]]:
        """Extract lat, long from Google Maps URL patterns."""
        # 1. @lat,long pattern e.g. @41.282117,69.215886,17z
        match = re.search(r"@(-?\d+\.\d+),(-?\d+\.\d+)", url)
        if match:
            return float(match.group(1)), float(match.group(2))

        # 2. !3dlat!4dlong pattern inside data params
        match = re.search(r"!3d(-?\d+\.\d+)!4d(-?\d+\.\d+)", url)
        if match:
            return float(match.group(1)), float(match.group(2))

        # 3. query param ?q=lat,long or ?ll=lat,long or ?query=lat,long
        parsed = urllib.parse.urlparse(url)
        params = urllib.parse.parse_qs(parsed.query)
        for key in ("q", "ll", "query", "center"):
            if key in params:
                val = params[key][0]
                coord_match = re.match(r"^(-?\d+\.\d+)\s*,\s*(-?\d+\.\d+)$", val.strip())
                if coord_match:
                    return float(coord_match.group(1)), float(coord_match.group(2))

        return None, None

    def extract_title_from_url(self, url: str) -> Optional[str]:
        """Extract place name from URL path /place/Place+Name/."""
        match = re.search(r"/maps/place/([^/@?]+)", url)
        if match:
            raw_title = match.group(1)
            unquoted = urllib.parse.unquote_plus(raw_title)
            # Remove any trailing junk
            cleaned = unquoted.strip()
            if cleaned and cleaned.lower() not in ("maps", "place", "search"):
                return cleaned
        return None

    def reverse_geocode(self, lat: float, lon: float) -> Dict[str, Any]:
        """Reverse geocode coordinates using OpenStreetMap Nominatim."""
        try:
            req_url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json&accept-language=uz,ru,en"
            resp = requests.get(req_url, headers=DEFAULT_HEADERS, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                address = data.get("address", {})
                display_name = data.get("display_name", "")

                road = address.get("road") or address.get("pedestrian") or ""
                house_number = address.get("house_number", "")
                suburb = address.get("suburb") or address.get("neighbourhood") or ""
                district = address.get("district") or address.get("city_district") or address.get("county") or ""
                city = address.get("city") or address.get("state") or address.get("region") or ""

                parts = [p for p in [road, house_number, suburb, district, city] if p]
                formatted_short = ", ".join(parts) if parts else display_name

                return {
                    "display_name": display_name,
                    "location_title": formatted_short,
                    "district_name": district or suburb,
                    "city_name": city,
                    "address_details": address,
                }
        except Exception as e:
            logger.warning(f"Reverse geocode failed for {lat}, {lon}: {e}")

        return {}

    def match_region_and_district(
        self,
        city_name: str = "",
        district_name: str = "",
        full_address: str = "",
    ) -> Tuple[Optional[Region], Optional[District]]:
        """Match database Region and District from address strings."""
        search_blob = f"{city_name} {district_name} {full_address}".lower()

        # Find Region
        matched_region = None
        for r in Region.objects.all():
            r_names = [r.name_uz, r.name_ru, r.name_en]
            for r_name in r_names:
                if not r_name:
                    continue
                clean_r = r_name.lower().replace("shahri", "").replace("viloyati", "").replace("область", "").strip()
                if clean_r and clean_r in search_blob:
                    matched_region = r
                    break
            if matched_region:
                break

        # Fallback to Tashkent if in Tashkent area
        if not matched_region:
            matched_region = Region.objects.filter(name_uz__icontains="Toshkent").first()

        # Find District within Region
        matched_district = None
        if matched_region:
            districts = District.objects.filter(region=matched_region)
            for d in districts:
                d_names = [d.name_uz, d.name_ru, d.name_en]
                for d_name in d_names:
                    if not d_name:
                        continue
                    clean_d = d_name.lower().replace("tumani", "").replace("район", "").replace("district", "").strip()
                    if clean_d and clean_d in search_blob:
                        matched_district = d
                        break
                if matched_district:
                    break

        return matched_region, matched_district

    def match_category(self, title: str = "", place_types: List[str] = None, fallback_id: Optional[int] = None) -> Optional[Category]:
        """Infer best matching Category from place title and types."""
        if fallback_id:
            cat = Category.objects.filter(id=fallback_id).first()
            if cat:
                return cat

        blob = f"{title} {' '.join(place_types or [])}".lower()

        # 1. Match against Category title directly
        for cat in Category.objects.all():
            titles = [cat.title, cat.title_uz, cat.title_ru, cat.title_en]
            for t in titles:
                if t and t.lower() in blob:
                    return cat

        # 2. Match against keyword mappings
        for cat_name, keywords in CATEGORY_KEYWORDS.items():
            for kw in keywords:
                if kw.lower() in blob:
                    cat = Category.objects.filter(
                        Q(title__icontains=cat_name)
                        | Q(title_uz__icontains=cat_name)
                        | Q(title_en__icontains=cat_name)
                    ).first()
                    if cat:
                        return cat

        # Default fallback to category 1 if exists
        return Category.objects.first()

    def parse_google_maps_url(self, raw_url: str, category_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Parse a Google Maps URL (canonical or short) into a structured place dictionary.
        """
        resolved_url = self.resolve_url(raw_url)
        lat, lon = self.extract_coordinates_from_url(resolved_url)
        title = self.extract_title_from_url(resolved_url)

        phone_number = None
        address = None
        website = None
        photo_urls = []
        rating = None

        # Fetch page HTML for richer metadata
        try:
            resp = requests.get(resolved_url, headers=DEFAULT_HEADERS, timeout=12)
            if resp.status_code == 200:
                html = resp.text

                # OpenGraph title fallback
                if not title:
                    og_title_m = re.search(r'<meta[^>]*property=["\']og:title["\'][^>]*content=["\']([^"\']+)["\']', html)
                    if og_title_m and og_title_m.group(1) not in ("Google Maps", "Google"):
                        title = og_title_m.group(1).split("·")[0].strip()

                # OpenGraph image
                og_img_m = re.search(r'<meta[^>]*property=["\']og:image["\'][^>]*content=["\']([^"\']+)["\']', html)
                if og_img_m:
                    photo_urls.append(og_img_m.group(1).replace("&amp;", "&"))

                # Additional photo extraction from HTML / JSON
                photos_found = re.findall(r'(https://lh[0-9]\.googleusercontent\.com/p/[A-Za-z0-9_-]+)', html)
                for p in photos_found:
                    full_p = p + "=w1200-h800-k-no"
                    if full_p not in photo_urls:
                        photo_urls.append(full_p)

                # Phone number in page
                phone_matches = re.findall(r'(\+?998[\s\d()-]{7,15})', html)
                if phone_matches:
                    phone_number = re.sub(r"[^\d+]", "", phone_matches[0])

                # Extract address from APP_INITIALIZATION_STATE if available
                app_init_m = re.search(r';window\.APP_INITIALIZATION_STATE\s*=\s*(.+?);window\.APP_FLAGS', html)
                if app_init_m:
                    try:
                        state_data = json.loads(app_init_m.group(1))
                        raw_blob = state_data[3][5]
                        if raw_blob.startswith(")]}'"):
                            raw_blob = raw_blob[5:].strip()
                        inner = json.loads(raw_blob)
                        if inner and isinstance(inner, list) and len(inner) > 0:
                            root = inner[0]
                            if not title and len(root) > 1 and isinstance(root[1], str):
                                title = root[1]
                            if (not lat or not lon) and len(root) > 2 and isinstance(root[2], list):
                                c = root[2][0]
                                if isinstance(c, list) and len(c) >= 3:
                                    lon, lat = float(c[1]), float(c[2])
                    except Exception as e_json:
                        logger.debug(f"Could not parse APP_INITIALIZATION_STATE: {e_json}")

        except Exception as e:
            logger.warning(f"Failed to fetch Google Maps page HTML: {e}")

        # Reverse geocoding if coordinates exist
        geo_info = {}
        if lat and lon:
            geo_info = self.reverse_geocode(lat, lon)

        location_title = geo_info.get("location_title") or address or ""
        region, district = self.match_region_and_district(
            city_name=geo_info.get("city_name", ""),
            district_name=geo_info.get("district_name", ""),
            full_address=geo_info.get("display_name", location_title),
        )

        category = self.match_category(title=title or "", fallback_id=category_id)

        return {
            "title": title or "Untitled Place",
            "lat": lat,
            "long": lon,
            "location_title": location_title,
            "phone_number": phone_number,
            "website": website,
            "category": category,
            "region": region,
            "district": district,
            "photo_urls": photo_urls,
            "rating": rating,
            "original_url": resolved_url,
        }

    def search_places(self, query: str, limit: int = 10, city: str = "Tashkent", category_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Search places via Google Places API (if key available) or Nominatim/OSM."""
        results = []

        # 1. Use Google Places API if key is present
        if self.api_key:
            try:
                search_url = (
                    "https://maps.googleapis.com/maps/api/place/textsearch/json"
                    f"?query={urllib.parse.quote_plus(query + ' in ' + city)}"
                    f"&key={self.api_key}"
                )
                resp = requests.get(search_url, timeout=12)
                if resp.status_code == 200:
                    data = resp.json()
                    for item in data.get("results", [])[:limit]:
                        geom = item.get("geometry", {}).get("location", {})
                        lat, lon = geom.get("lat"), geom.get("lng")
                        name = item.get("name")
                        address = item.get("formatted_address")
                        types = item.get("types", [])

                        photo_urls = []
                        for ph in item.get("photos", [])[:3]:
                            ref = ph.get("photo_reference")
                            if ref:
                                photo_urls.append(
                                    f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=1200&photoreference={ref}&key={self.api_key}"
                                )

                        region, district = self.match_region_and_district(full_address=address or "")
                        category = self.match_category(title=name, place_types=types, fallback_id=category_id)

                        results.append({
                            "title": name,
                            "lat": lat,
                            "long": lon,
                            "location_title": address,
                            "phone_number": None,
                            "website": None,
                            "category": category,
                            "region": region,
                            "district": district,
                            "photo_urls": photo_urls,
                            "rating": item.get("rating"),
                        })
                    return results
            except Exception as e:
                logger.error(f"Google Places API search failed: {e}")

        # 2. Fallback to OpenStreetMap Nominatim search (Free, No Key Required)
        try:
            search_query = f"{query} in {city}"
            req_url = f"https://nominatim.openstreetmap.org/search?q={urllib.parse.quote_plus(search_query)}&format=json&addressdetails=1&limit={limit}&accept-language=uz,ru,en"
            resp = requests.get(req_url, headers=DEFAULT_HEADERS, timeout=12)
            if resp.status_code == 200:
                for item in resp.json():
                    lat = float(item.get("lat")) if item.get("lat") else None
                    lon = float(item.get("lon")) if item.get("lon") else None
                    display_name = item.get("display_name", "")
                    name = item.get("name") or display_name.split(",")[0].strip()

                    addr = item.get("address", {})
                    road = addr.get("road", "")
                    district_name = addr.get("district") or addr.get("suburb", "")
                    city_name = addr.get("city") or addr.get("state", "")
                    parts = [p for p in [road, district_name, city_name] if p]
                    location_title = ", ".join(parts) if parts else display_name

                    region, district = self.match_region_and_district(
                        city_name=city_name,
                        district_name=district_name,
                        full_address=display_name,
                    )
                    category = self.match_category(title=name, fallback_id=category_id)

                    # Map image static link
                    photo_urls = []
                    if lat and lon:
                        static_map = f"https://maps.google.com/maps/api/staticmap?center={lat},{lon}&zoom=16&size=800x600&sensor=false"
                        photo_urls.append(static_map)

                    results.append({
                        "title": name,
                        "lat": lat,
                        "long": lon,
                        "location_title": location_title,
                        "phone_number": None,
                        "website": None,
                        "category": category,
                        "region": region,
                        "district": district,
                        "photo_urls": photo_urls,
                        "rating": None,
                    })
        except Exception as e:
            logger.error(f"Nominatim place search failed: {e}")

        return results

    def save_place_to_post(self, place_data: Dict[str, Any], owner=None) -> Post:
        """
        Create and persist a Post instance from parsed place dictionary.
        """
        category = place_data.get("category")
        if not category and place_data.get("category_id"):
            category = Category.objects.filter(id=place_data["category_id"]).first()

        region = place_data.get("region")
        district = place_data.get("district")

        title = place_data.get("title") or "Unnamed Place"
        location_title = place_data.get("location_title") or ""
        phone_number = place_data.get("phone_number") or ""
        lat = place_data.get("lat")
        long = place_data.get("long")

        # Create or update post based on title + coordinates/location
        post = None
        if lat and long:
            post = Post.objects.filter(
                title=title,
                lat__range=(lat - 0.001, lat + 0.001),
                long__range=(long - 0.001, long + 0.001),
            ).first()

        if not post:
            post = Post.objects.create(
                owner=owner,
                title=title,
                location_title=location_title,
                phone_number=phone_number,
                lat=lat,
                long=long,
                category=category,
                region=region,
                district=district,
                state="ACCEPTED",
                description=place_data.get("description") or f"Place imported from Google Maps: {title}",
            )
        else:
            # Update fields if missing
            if location_title and not post.location_title:
                post.location_title = location_title
            if phone_number and not post.phone_number:
                post.phone_number = phone_number
            if category and not post.category:
                post.category = category
            if region and not post.region:
                post.region = region
            if district and not post.district:
                post.district = district
            post.save()

        # Add Website / Social Media Link if present
        website = place_data.get("website")
        if website:
            if not post.social_links.filter(link=website).exists():
                PostSocialMedia.objects.create(post=post, type="WEBSITE", link=website)

        # Download & attach photos to PostImage
        photo_urls = place_data.get("photo_urls") or []
        for p_url in photo_urls[:3]:
            try:
                resp = requests.get(p_url, headers=DEFAULT_HEADERS, timeout=10)
                if resp.status_code == 200 and len(resp.content) > 1024:
                    fname = f"post_{post.id}_{os.path.basename(p_url.split('?')[0]) or 'photo'}.jpg"
                    post_img = PostImage(post=post)
                    post_img.image.save(fname, ContentFile(resp.content), save=True)
            except Exception as e:
                logger.warning(f"Could not download photo for post {post.id} from {p_url}: {e}")

        return post
