from django.db import migrations
from django.db import models

import constance.models


class Migration(migrations.Migration):
    dependencies = [
        ('constance', '0002_migrate_from_old_table'),
    ]

    operations = [
        migrations.AddField(
            model_name='constance',
            name='value_json',
            field=models.JSONField(
                blank=True,
                decoder=constance.models.ConstanceDecoder,
                default=None,
                encoder=constance.models.ConstanceEncoder,
                null=True,
            ),
        ),
    ]
