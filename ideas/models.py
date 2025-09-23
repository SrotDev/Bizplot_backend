from django.db import models
from django.conf import settings
import uuid

# Create your models here.


class Idea(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

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
        ("retail", "Retail"),
        ("ecommerce", "E-commerce"),
        ("saas", "SaaS"),
        ("service", "Service"),
        ("other", "Other"),
    ]
    product_category = models.CharField(max_length=50, choices=PRODUCT_CATEGORIES, default="other")


    TARGET_MARKETS = [
        ("local", "Local"),
        ("regional", "Regional"),
        ("global", "Global"),
    ]
    target_market = models.CharField(max_length=20, choices=TARGET_MARKETS, default="local")


    business_plan = models.TextField(blank=True, default="")

    created_at = models.DateTimeField(auto_now_add=True)



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
    title = models.CharField(max_length=200)
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
    product_service = models.JSONField(default=dict, blank=True)  
    business_model = models.JSONField(default=dict, blank=True)  
    go_to_market = models.JSONField(default=dict, blank=True)  
    traction = models.JSONField(default=dict, blank=True)  
    financial_projection = models.JSONField(default=dict, blank=True)  
    roadmap = models.JSONField(default=list, blank=True)  
    team = models.JSONField(default=list, blank=True)  
    risks_opportunities = models.JSONField(default=dict, blank=True)  
    ask_funding = models.JSONField(default=dict, blank=True)  

    # Meta flags
    premium_locked = models.BooleanField(default=False)
    regeneration_allowed = models.BooleanField(default=True)
    tags = models.JSONField(default=list, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
