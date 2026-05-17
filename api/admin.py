from django.contrib import admin
from .models import UserProfile, Level, Module, Exercise, UserProgress

admin.site.site_header = "PyLearn — Administration"
admin.site.site_title = "PyLearn Admin"

@admin.register(Level)
class LevelAdmin(admin.ModelAdmin):
    list_display = ('order', 'icon', 'title', 'slug')
    ordering = ('order',)

class ExerciseInline(admin.TabularInline):
    model = Exercise
    extra = 1

@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('title', 'level', 'order', 'xp_reward', 'duration_min')
    list_filter = ('level',)
    inlines = [ExerciseInline]
    ordering = ('level__order', 'order')

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'xp_total', 'level_badge', 'streak_days', 'created_at')

@admin.register(UserProgress)
class UserProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'module', 'completed', 'completed_at')
    list_filter = ('completed', 'module__level')
