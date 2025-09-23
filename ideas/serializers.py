from rest_framework import serializers
from django.contrib.auth import get_user_model

from ideas.models import Idea, IdeaCard

User = get_user_model()





class IdeaCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = IdeaCard
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]
        extra_kwargs = {
            "idea": {"required": False},
        }


class IdeaCardBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = IdeaCard
        fields = ["id", "startup_idea", "summary", "quick_stats", "model_archetype", "generation_status"]


class IdeaSerializer(serializers.ModelSerializer):

    class Meta:
        model = Idea
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at", "user"]
        extra_kwargs = {
            "startup_idea": {"required": True},
        }