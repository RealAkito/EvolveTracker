from django.contrib import admin
from EvolveTracker.apps.bugs.models import Issue, Comment
# Register your models here.

admin.site.register(Issue)
admin.site.register(Comment)