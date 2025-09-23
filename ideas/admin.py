from django.contrib import admin

# Register your models here.

from .models import Idea, IdeaCard

admin.site.register(Idea)
admin.site.register(IdeaCard)