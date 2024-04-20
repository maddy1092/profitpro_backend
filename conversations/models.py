from django.db import models
from django.utils.translation import gettext_lazy as _

from users.models import User


states = (
    ('IN_PROGRESS', 'in_progress'),
    ('CLOSED', 'closed'),       
)

# User = get_user_model()
class Dialog(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    state = models.CharField(max_length=100, default="CLOSED")

    class Meta:
        verbose_name = _("Dialog")
        verbose_name_plural = _("Dialogs")

class Conversation(models.Model):

    conversation_id = models.AutoField(primary_key=True)
    conversation_link = models.CharField(max_length=250, blank=True)
    speaker_type = models.CharField(max_length=30, blank=True)
    transcript = models.TextField(blank=True)
    dialog_id = models.ForeignKey(Dialog, on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now=True, blank=True)
    modified_date = models.DateTimeField(auto_now=True, blank=True)
    duration = models.FloatField(blank=True, null=True)

    class Meta:
        verbose_name = _("Conversation")
        verbose_name_plural = _("Conversations")

