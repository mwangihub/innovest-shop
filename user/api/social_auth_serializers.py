from rest_framework import serializers
from allauth.socialaccount.models import SocialApp


class SocialAppSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialApp
        fields = ["provider", "name", "client_id", "secret", ]
