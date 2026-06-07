import os
import re

from django.conf import settings
from django.core.management.base import BaseCommand

from apps.posts.models import Category

CATEGORY_SUBDIR = "category_images"
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".gif"}


def title_from_filename(stem: str) -> str:
    """Turn a filename like 'IceSkating' or 'Tennis_Court' into 'Ice Skating' / 'Tennis Court'."""
    # underscores / dashes -> spaces
    name = re.sub(r"[_\-]+", " ", stem)
    # split camelCase boundaries (lower/digit followed by upper), e.g. IceSkating -> Ice Skating
    name = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", name)
    name = re.sub(r"\s+", " ", name).strip()
    # Title-case words, but leave all-caps short tokens (CS, PS) as-is
    words = [w if (w.isupper() and len(w) <= 3) else w.capitalize() for w in name.split(" ")]
    return " ".join(words)


class Command(BaseCommand):
    help = "Create Category rows for every image already present in media/category_images/."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be created without writing to the DB.",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        media_dir = os.path.join(settings.MEDIA_ROOT, CATEGORY_SUBDIR)

        if not os.path.isdir(media_dir):
            self.stderr.write(self.style.ERROR(f"Directory not found: {media_dir}"))
            return

        files = sorted(
            f for f in os.listdir(media_dir)
            if os.path.isfile(os.path.join(media_dir, f))
            and os.path.splitext(f)[1].lower() in IMAGE_EXTS
        )

        if not files:
            self.stderr.write(self.style.WARNING(f"No image files found in {media_dir}"))
            return

        created, skipped = 0, 0
        for filename in files:
            image_path = f"{CATEGORY_SUBDIR}/{filename}"  # relative to MEDIA_ROOT, as ImageField stores it
            title = title_from_filename(os.path.splitext(filename)[0])

            # Idempotent: keyed on the image path so re-running won't duplicate rows.
            if Category.objects.filter(image=image_path).exists():
                self.stdout.write(f"  skip (exists): {title}  <- {image_path}")
                skipped += 1
                continue

            if dry_run:
                self.stdout.write(f"  would create: {title}  <- {image_path}")
                created += 1
                continue

            Category.objects.create(title=title, image=image_path)
            self.stdout.write(self.style.SUCCESS(f"  created: {title}  <- {image_path}"))
            created += 1

        verb = "would be created" if dry_run else "created"
        self.stdout.write(self.style.SUCCESS(f"\nDone. {created} {verb}, {skipped} skipped."))