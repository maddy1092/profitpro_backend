# Generated by Django 4.2.4 on 2023-08-17 21:15

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("conversations", "0008_remove_conversation_transcript_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="conversation",
            name="user_id",
        ),
        migrations.AlterField(
            model_name="conversation",
            name="created_date",
            field=models.DateTimeField(auto_now=True),
        ),
    ]
