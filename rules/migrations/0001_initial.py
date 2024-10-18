# Generated by Django 5.1.2 on 2024-10-17 15:32

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Node",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "type",
                    models.CharField(
                        choices=[("operator", "Operator"), ("operand", "Operand")],
                        max_length=10,
                    ),
                ),
                (
                    "operator",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("AND", "AND"),
                            ("OR", "OR"),
                            (">", "Greater than"),
                            ("<", "Less than"),
                            ("=", "Equal"),
                        ],
                        max_length=3,
                        null=True,
                    ),
                ),
                ("value", models.CharField(blank=True, max_length=255, null=True)),
                (
                    "left",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="left_child",
                        to="rules.node",
                    ),
                ),
                (
                    "right",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="right_child",
                        to="rules.node",
                    ),
                ),
            ],
        ),
    ]