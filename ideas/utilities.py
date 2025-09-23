from __future__ import annotations

from .models import Idea,IdeaCard
from .serializers import IdeaCardSerializer, IdeaSerializer

from chatbots.gemini_api import GeminiAPIManager

from django.contrib.auth import get_user_model

from accounts.models import CustomUser

from chatbots.montecarlo import start_simulation


def generate_brief_ideacards(idea: Idea, ideacards_list: list[IdeaCard], user: CustomUser):
    
    
    ideacard = None
    ai_res = None
    if(idea.business_plan.strip() == ""):
        ai_res = GeminiAPIManager.process_user_request(IdeaSerializer(idea).data, agent_type=1, has_pdf=True)
    else:
        ai_res = GeminiAPIManager.process_user_request(IdeaSerializer(idea).data, agent_type=1, has_pdf=False)

    ideacards = ai_res.get("ideas", [])
    
    ind = 0
    
    for ideacard_dict in ideacards:
        ideacard_serializer = IdeaCardSerializer(ideacards_list[ind], data=ideacard_dict)
        ideacard_serializer.is_valid(raise_exception=True)
        # ideacard = IdeaCard.objects.create(idea=idea, **ideacard_serializer.validated_data)
        
        ideacard = ideacard_serializer.save()
        # ideacard.save()

        ind+=1

    user.api_tokens_used += int(ai_res.get("total_used_tokens_for_gemini_api", 0))
    user.save()



def generate_detailed_ideacard(ideacard: IdeaCard, user: CustomUser):
    try:

        ideacard_serializer = IdeaCardSerializer(ideacard)
        ai_params = ideacard_serializer.data
        ai_params["business_plan"] = ideacard.idea.business_plan
        ai_params["target_audience"] = ideacard.quick_stats.get("target_audience", "")
        ai_params["budget_range"] = ideacard.idea.budget_range
        ai_params["target_market"] = ideacard.idea.target_market

        ai_res = GeminiAPIManager.process_user_request(ai_params, agent_type=2)


        montecarlo = start_simulation(param_ranges=ai_res["data_for_montecarlo_simulation"])

        ai_res["montecarlo_chart"] = montecarlo

        ideacard_serializer = IdeaCardSerializer(ideacard, data=ai_res, partial=True)
        ideacard_serializer.is_valid(raise_exception=True)
        ideacard = ideacard_serializer.save()
        ideacard.generation_status = "completed"
        ideacard.save()

        user.api_tokens_used += int(ai_res.get("total_used_tokens_for_gemini_api", 1))
        user.save()

    except Exception as e:
        print(f"Exception occurred in generate_detailed_ideacard: {e}")
        ideacard.generation_status = "failed"
        ideacard.save()