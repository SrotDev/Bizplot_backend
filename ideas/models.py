from django.db import models
from django.conf import settings
import uuid

# Create your models here.

from django.contrib.auth import get_user_model

User = get_user_model() # Reference the custom user model


class Idea(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="ideas")

    title = models.CharField(max_length=200, blank=False, null=False, default="")
    short_description = models.TextField(blank=True, null=False, default="")


    BUDGET_CHOICES = [
        ("<1k", "< $1k"),
        ("1k-10k", "$1k–10k"),
        ("10k-50k", "$10k–50k"),
        ("50k-100k", "$50k–100k"),
        ("100k-500k", "$100k–500k"),
        ("500k-1M", "$500k–$1M"),
        (">1M", "> $1M"),  
    ]
    budget_range = models.CharField(max_length=20, choices=BUDGET_CHOICES, default="<1k")

    PRODUCT_CATEGORIES = [
        ("saas", "Software / SaaS"),
        ("mobile_app", "Mobile App"),
        ("ai_ml", "AI / Machine Learning"),
        ("web_platform", "Web Platform / Marketplace"),
        ("ecommerce", "E-commerce / Retail"),
        ("fintech", "FinTech / Payments"),
        ("healthtech", "HealthTech / MedTech"),
        ("edtech", "EdTech / Learning"),
        ("greentech", "GreenTech / Sustainability"),
        ("agritech", "AgriTech / FoodTech"),
        ("hardware_iot", "Hardware / IoT / Robotics"),
        ("ar_vr", "AR / VR / Metaverse"),
        ("media_gaming", "Media / Entertainment / Gaming"),
        ("travel_hospitality", "Travel / Hospitality"),
        ("social_impact", "Social Impact / Nonprofit"),
        ("other", "Other"),
    ]

    product_category = models.CharField(max_length=50, choices=PRODUCT_CATEGORIES, default="other")


    TARGET_MARKETS = [
        ("b2c", "B2C – Mass Consumers"),
        ("b2b_small", "B2B – Small Businesses / Startups"),
        ("b2b_enterprise", "B2B – Enterprise / Corporates"),
        ("b2g", "B2G – Government / NGOs"),
        ("students", "Students / Education Sector"),
        ("healthcare", "Healthcare Professionals / Hospitals"),
        ("freelancers", "Freelancers / Creators"),
        ("developers", "Developers / Tech Teams"),
        ("rural", "Rural / Underserved Communities"),
        ("luxury", "Luxury / Premium Customers"),
    ]
    target_market = models.CharField(max_length=20, choices=TARGET_MARKETS, default="local")


    business_plan = models.TextField(blank=True, default="")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)



    def __str__(self):
        return self.title


    @property
    def cards(self):
        """Return all IdeaCards related to this Idea"""
        return self.ideacard_set.all()  # default reverse relation






class IdeaCard(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    idea = models.ForeignKey("Idea", on_delete=models.CASCADE, related_name="cards")

    generation_status = models.CharField(
        max_length=20,
        choices=[
            ("not_started_yet", "Not Started Yet"),
            ("pending","Pending"),
            ("in_progress","In Progress"),
            ("completed","Completed"),
            ("failed","Failed")
        ],
        default="not_started_yet"
    )

    # Basic info
    startup_idea = models.CharField(max_length=200)
    summary = models.TextField(blank=True, null=True)
    tagline = models.TextField(blank=True, null=True)
    model_type = models.CharField(
        max_length=50,
        choices=[("retail","Retail"),("ecommerce","E-commerce"),("saas","SaaS"),("service","Service"),("other","Other")],
        default="other"
    )
    problem_statement = models.TextField(blank=True, null=True)
    solution = models.TextField(blank=True, null=True)

    # New fields from JSON snippet
    quick_stats = models.JSONField(default=dict, blank=True)  
    model_archetype = models.CharField(max_length=100, blank=True, null=True)  # e.g., "B2C/B2B SaaS"

    # Nested sections as JSON
    market_analysis = models.JSONField(default=dict, blank=True)  
    competitor_analysis = models.JSONField(default=dict, blank=True)
    product_service = models.JSONField(default=dict, blank=True)  
    business_model = models.JSONField(default=dict, blank=True)  
    go_to_market = models.JSONField(default=dict, blank=True)  
    traction = models.JSONField(default=dict, blank=True)  
    financial_projection = models.JSONField(default=dict, blank=True)  
    roadmap = models.JSONField(default=list, blank=True)  
    team = models.JSONField(default=list, blank=True)  
    risks_opportunities = models.JSONField(default=dict, blank=True)  
    ask_funding = models.JSONField(default=dict, blank=True)  


    chart = models.JSONField(default=dict, blank=True)  # e.g., {"type": "bar", "data": {...}, "layout": {...}}

    data_for_montecarlo_simulation = models.JSONField(default=dict, blank=True)  # e.g., {"assumptions": {...}, "results": {...}}

    # Meta flags
    premium_locked = models.BooleanField(default=False)
    regeneration_allowed = models.BooleanField(default=True)
    tags = models.JSONField(default=list, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.startup_idea
    



