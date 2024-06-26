# Generated by Django 4.2.4 on 2023-08-17 15:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("conversations", "0005_remove_dialog_conversation_id"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="dialog",
            options={"verbose_name": "Dialog", "verbose_name_plural": "Dialogs"},
        ),
        migrations.AddField(
            model_name="conversation",
            name="dialog_id",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                to="conversations.dialog",
            ),
        ),
    ]
