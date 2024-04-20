from rest_framework import serializers
from users.models import User


class UserSerializer(serializers.ModelSerializer):
  class Meta:
    model = User
    fields = (
      "user_id",
      "user_email",
      "user_display_name",
      "first_name",
      "last_name",
      "role",
      "city",
      "address1",
      "address2",
      "about",
      "dealer_name",
      "email",
      "is_update",
      "lot_address",
      "notes",
      "phone",
      "state",
      "token",
      "userImage",
      "user_avatar",
      "user_nicename",
      "zipcode"
    )

