# Generated by Django 5.1.2 on 2024-10-18 06:09

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("rules", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="node",
            name="parent",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="parent_node",
                to="rules.node",
            ),
        ),
        migrations.AlterField(
            model_name="node",
            name="left",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="left_node",
                to="rules.node",
            ),
        ),
        migrations.AlterField(
            model_name="node",
            name="operator",
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name="node",
            name="right",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="right_node",
                to="rules.node",
            ),
        ),
        migrations.AlterField(
            model_name="node",
            name="type",
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name="node",
            name="value",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]