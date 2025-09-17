from rest_framework import serializers
from .models import Meep, Profile

class MeepSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meep
        fields = ["id", "user", "body", "created_at"]

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = [
            "id",
            "user",
            "profile_bio",
            "homepage_link",
            "facebook_link",
            "instagram_link",
            "linkedin_link",
            "profile_image",
            "created_at",
        ]
