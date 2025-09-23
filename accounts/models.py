from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid

# Create your models here.


class CustomUser(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)



    email = models.EmailField(unique=True, null=False, blank=False)
    full_name = models.CharField(max_length=100, null=False, blank=True, default='')
    profile_picture = models.URLField(blank=True, null=True)




    BUSINESS_STAGES = [
        ("idea", "Idea"),
        ("early", "Early Startup"),
        ("scaling", "Scaling"),
        ("established", "Established"),
    ]

    business_stage = models.CharField(max_length=20, choices=BUSINESS_STAGES, default="idea")
    industry = models.CharField(max_length=100, blank=True, null=True)
    target_market = models.CharField(max_length=50, blank=True, null=True)
    skills_background = models.TextField(blank=True, null=True)
    budget_range = models.CharField(
        max_length=20,
        choices=[("<1k", "< $1k"), ("1k-10k", "$1k–10k"), ("10k-50k", "$10k–50k"), (">50k", "> $50k")],
        default="<1k"
    )



    subscription_plan = models.CharField(
        max_length=20,
        choices=[("free", "Free"), ("pro", "Pro"), ("enterprise", "Enterprise")],
        default="free"
    )
    api_tokens_used = models.PositiveIntegerField(default=0)
    ideas_created = models.PositiveIntegerField(default=0)
    messages_sent = models.PositiveIntegerField(default=0)


    two_factor_enabled = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)


    USERNAME_FIELD = "email"   # login with email
    REQUIRED_FIELDS = ["username"]  # keep username for admin compatibility

    def __str__(self):
        return self.full_name



