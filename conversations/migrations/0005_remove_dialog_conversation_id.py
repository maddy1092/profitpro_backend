# Generated by Django 4.2.4 on 2023-08-17 15:03

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("conversations", "0004_alter_conversation_created_date_dialog"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="dialog",
            name="conversation_id",
        ),
    ]