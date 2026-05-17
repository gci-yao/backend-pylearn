from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True, default='')
    avatar_url = models.URLField(blank=True, default='')
    xp_total = models.IntegerField(default=0)
    streak_days = models.IntegerField(default=0)
    last_activity = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Profil de {self.user.username}"

    @property
    def level_badge(self):
        xp = self.xp_total
        if xp >= 500: return 'Expert'
        if xp >= 200: return 'Avancé'
        if xp >= 80: return 'Intermédiaire'
        return 'Débutant'


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.get_or_create(user=instance)


class Level(models.Model):
    slug = models.SlugField(unique=True)
    title = models.CharField(max_length=100)
    description = models.TextField(default='')
    color = models.CharField(max_length=30, default='#E1F5EE')
    text_color = models.CharField(max_length=30, default='#085041')
    accent = models.CharField(max_length=30, default='#1D9E75')
    order = models.PositiveIntegerField(default=0)
    icon = models.CharField(max_length=10, default='🐍')

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title


class Module(models.Model):
    level = models.ForeignKey(Level, on_delete=models.CASCADE, related_name='modules')
    title = models.CharField(max_length=200)
    description = models.TextField(default='')
    concept = models.TextField(default='')
    code_example = models.TextField(default='')
    icon = models.CharField(max_length=50, default='code')
    order = models.PositiveIntegerField(default=0)
    xp_reward = models.IntegerField(default=10)
    duration_min = models.IntegerField(default=15)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"[{self.level.title}] {self.title}"


class Exercise(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='exercises')
    text = models.TextField()
    hint = models.TextField(blank=True, default='')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"Ex.{self.order} - {self.module.title}"


class UserProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='progress')
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='completions')
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True, default='')

    class Meta:
        unique_together = ('user', 'module')

    def __str__(self):
        status = '✓' if self.completed else '○'
        return f"{status} {self.user.username} — {self.module.title}"
