from rest_framework import serializers
from allauth.socialaccount.models import SocialApp


# D:\Projects\DJANGO_SHOP\env\Lib\site-packages\allauth\socialaccount\models.py

class SocialAppSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialApp
        fields = ["provider", "name", "client_id", "secret", ]
