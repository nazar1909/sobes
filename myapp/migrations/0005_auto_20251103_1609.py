from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0004_add_place_field'),
    ]

    operations = [
        migrations.AddField(
            model_name='ad',
            name='slug',
            field=models.SlugField(max_length=120, unique=True, blank=True),
        ),
    ]
