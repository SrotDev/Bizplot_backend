from django.shortcuts import render

from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.permissions import *

from ideas.utilities import generate_brief_ideacards, generate_detailed_ideacard
from .models import Idea, IdeaCard
from .serializers import IdeaSerializer, IdeaCardSerializer
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated


import threading
# Create your views here.


class IdeaListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        ideas = Idea.objects.filter(user=request.user)
        serializer = IdeaSerializer(ideas, many=True)
        return Response(serializer.data, status=200)
    



class IdeaViewSet(viewsets.ModelViewSet):
    queryset = Idea.objects.all()
    serializer_class = IdeaSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        idea = serializer.save(user=self.request.user)

        ideacards = []

        for i in range(3):
            ideacard = IdeaCard.objects.create(idea = idea)
            ideacards.append(ideacard)

        # Run generate_brief_ideacards in a separate thread with parameters
        thread = threading.Thread(target=generate_brief_ideacards, args=(idea, ideacards, self.request.user), daemon=True)
        thread.start()

        # generate_brief_ideacards(idea, ideacards, self.request.user)

        # Get the three related IdeaCards

        idea_cards_data = IdeaCardSerializer(ideacards, many=True).data
        self.idea_cards_data = idea_cards_data  # Store for use in create()

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        # Attach the idea cards data to the response if available
        if hasattr(self, 'idea_cards_data'):
            response.data['idea_cards'] = self.idea_cards_data
        return response
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        idea_cards = IdeaCard.objects.filter(idea=instance)
        idea_cards_data = IdeaCardSerializer(idea_cards, many=True).data
        data = serializer.data
        data['idea_cards'] = idea_cards_data
        return Response(data)



class IdeaCardGenerateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        idea_card_id = kwargs.get("pk")
        idea_card = IdeaCard.objects.get(id=idea_card_id)

        if idea_card.generation_status=="not_started_yet":
            idea_card.generation_status = "pending"
            idea_card.save()
            thread = threading.Thread(target=generate_detailed_ideacard, args=(idea_card,  self.request.user), daemon=True)
            thread.start()
            # generate_detailed_ideacard(idea_card, request.user)


        idea_card_serializer = IdeaCardSerializer(idea_card)
        # user = request.user
        # generate_brief_ideacards(idea, user)
        return Response(idea_card_serializer.data, status=200)
    

class IdeaCardViewSet(viewsets.ModelViewSet):

    queryset = IdeaCard.objects.all()
    serializer_class = IdeaCardSerializer
    permission_classes = [IsAdminUser]


