import json
from django.shortcuts import render
from rest_framework.response import Response
from ideas.serializers import *

# Create your views here.
from .chat_and_comparison import chat_bot, compare_answers

class ChatbotView:
    permission_classes = ["IsAuthenticated"]
    def post(self, request):
        # Handle POST request for chatbot interaction
        data = request.data
        params = {}

        params["prev_response"] = data.history
        params["current_q"] = data.current_q

        idea = IdeaCard.objects.get(id=data.idea_id)
        idea_serializer = IdeaCardBriefSerializer(idea)

        params["idea"] = json.dumps(idea_serializer.data)

        new_history = chat_bot(params)

        

        response = new_history
        return Response(response)
