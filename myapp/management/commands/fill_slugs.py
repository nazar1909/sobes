from django.core.management.base import BaseCommand
from django.utils.text import slugify
from unidecode import unidecode
from myapp.models import AD
import uuid

class Command(BaseCommand):
    help = "Fill empty slugs for AD objects."

    def handle(self, *args, **options):
        qs = AD.objects.filter(slug__isnull=True) | AD.objects.filter(slug='')
        count = qs.count()
        self.stdout.write(f"Found {count} ADs with empty slug.")

        for ad in qs:
            base = slugify(unidecode(ad.title)) if ad.title else 'ad'
            # trim to field length minus reserve
            max_len = ad._meta.get_field('slug').max_length
            base = base[: max_len - 8]
            candidate = base
            i = 1
            while AD.objects.filter(slug=candidate).exclude(pk=ad.pk).exists():
                candidate = f"{base}-{i}"
                i += 1
                if i > 50:
                    candidate = f"{base}-{uuid.uuid4().hex[:6]}"
                    break
            ad.slug = candidate
            ad.save()
            self.stdout.write(f"Set slug for AD(id={ad.pk}) -> {ad.slug}")

        self.stdout.write("Done.")
