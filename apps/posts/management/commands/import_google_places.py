import os
from django.core.management.base import BaseCommand
from apps.posts.models import Category
from apps.posts.services import GoogleMapsParserService


class Command(BaseCommand):
    help = "Parse places from Google Maps and import them into the Post model."

    def add_arguments(self, parser):
        parser.add_argument(
            "--url",
            type=str,
            help="Google Maps Place URL (canonical or short maps.app.goo.gl link).",
        )
        parser.add_argument(
            "--file",
            type=str,
            help="Path to a text file containing Google Maps URLs (one per line).",
        )
        parser.add_argument(
            "--query",
            type=str,
            help="Search query to find and import places (e.g. 'Football in Tashkent').",
        )
        parser.add_argument(
            "--category",
            type=str,
            help="Category ID or Category title (e.g. '1' or 'Football').",
        )
        parser.add_argument(
            "--city",
            type=str,
            default="Tashkent",
            help="City for search queries (default: 'Tashkent').",
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=10,
            help="Maximum number of places to import when querying (default: 10).",
        )

    def handle(self, *args, **options):
        url = options.get("url")
        file_path = options.get("file")
        query = options.get("query")
        category_arg = options.get("category")
        city = options.get("city") or "Tashkent"
        limit = options.get("limit") or 10

        parser_service = GoogleMapsParserService()

        # Resolve category if provided
        category = None
        if category_arg:
            if category_arg.isdigit():
                category = Category.objects.filter(id=int(category_arg)).first()
            if not category:
                category = Category.objects.filter(title__icontains=category_arg).first()
            if not category:
                self.stdout.write(self.style.WARNING(f"Category '{category_arg}' not found. Will auto-detect from place names."))
            else:
                self.stdout.write(self.style.SUCCESS(f"Using category: {category.title} (ID: {category.id})"))

        category_id = category.id if category else None

        # 1. Single URL Mode
        if url:
            self.stdout.write(f"Parsing Google Maps URL: {url}...")
            place_data = parser_service.parse_google_maps_url(url, category_id=category_id)
            post = parser_service.save_place_to_post(place_data)
            self.stdout.write(self.style.SUCCESS(
                f"Successfully imported Post #{post.id}: '{post.title}'\n"
                f"  Location: {post.location_title}\n"
                f"  Category: {post.category}\n"
                f"  Coordinates: {post.lat}, {post.long}\n"
                f"  Region: {post.region} / District: {post.district}"
            ))
            return

        # 2. File with URLs Mode
        if file_path:
            if not os.path.exists(file_path):
                self.stdout.write(self.style.ERROR(f"File not found: {file_path}"))
                return
            with open(file_path, "r", encoding="utf-8") as f:
                urls = [line.strip() for line in f if line.strip() and not line.startswith("#")]

            self.stdout.write(f"Found {len(urls)} URLs in {file_path}. Processing...")
            count = 0
            for u in urls:
                try:
                    self.stdout.write(f"Parsing: {u}...")
                    place_data = parser_service.parse_google_maps_url(u, category_id=category_id)
                    post = parser_service.save_place_to_post(place_data)
                    count += 1
                    self.stdout.write(self.style.SUCCESS(f"[{count}/{len(urls)}] Imported Post #{post.id}: {post.title}"))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error importing {u}: {e}"))

            self.stdout.write(self.style.SUCCESS(f"Finished! Successfully imported {count} places."))
            return

        # 3. Search Query Mode
        if query:
            self.stdout.write(f"Searching for places matching '{query}' in {city} (limit: {limit})...")
            places = parser_service.search_places(query=query, limit=limit, city=city, category_id=category_id)
            if not places:
                self.stdout.write(self.style.WARNING("No places found for query."))
                return

            self.stdout.write(f"Found {len(places)} places. Importing into Post model...")
            count = 0
            for item in places:
                try:
                    post = parser_service.save_place_to_post(item)
                    count += 1
                    self.stdout.write(self.style.SUCCESS(f"[{count}/{len(places)}] Imported Post #{post.id}: {post.title}"))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Failed to save place '{item.get('title')}': {e}"))

            self.stdout.write(self.style.SUCCESS(f"Finished! Successfully imported {count} places."))
            return

        self.stdout.write(self.style.ERROR(
            "Please provide at least one option: --url <URL>, --file <FILE>, or --query <SEARCH_QUERY>."
        ))
