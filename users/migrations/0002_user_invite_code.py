# Generated by Django 5.0.1 on 2024-02-14 07:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="invite_code",
            field=models.CharField(
                blank=True, max_length=6, null=True, verbose_name="инвайт-код"
            ),
        ),
    ]
