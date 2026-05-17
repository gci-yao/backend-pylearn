from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile, Level, Module, Exercise, UserProgress


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    password2 = serializers.CharField(write_only=True)
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password', 'password2')

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Cet email est déjà utilisé.")
        return value.lower()

    def validate_username(self, value):
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("Ce nom d'utilisateur est déjà pris.")
        return value

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({'password2': "Les mots de passe ne correspondent pas."})
        return data

    def create(self, validated_data):
        validated_data.pop('password2')
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    level_badge = serializers.ReadOnlyField()

    class Meta:
        model = UserProfile
        fields = ('bio', 'avatar_url', 'xp_total', 'streak_days', 'created_at', 'level_badge')


class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)
    modules_completed = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'full_name', 'profile', 'modules_completed')

    def get_modules_completed(self, obj):
        return obj.progress.filter(completed=True).count()

    def get_full_name(self, obj):
        return obj.get_full_name() or obj.username


class ExerciseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exercise
        fields = ('id', 'text', 'hint', 'order')


class ModuleSerializer(serializers.ModelSerializer):
    exercises = ExerciseSerializer(many=True, read_only=True)
    is_completed = serializers.SerializerMethodField()
    level_title = serializers.CharField(source='level.title', read_only=True)
    level_slug = serializers.CharField(source='level.slug', read_only=True)

    class Meta:
        model = Module
        fields = ('id', 'title', 'description', 'concept', 'code_example', 'icon',
                  'order', 'xp_reward', 'duration_min', 'exercises',
                  'is_completed', 'level_title', 'level_slug')

    def get_is_completed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.completions.filter(user=request.user, completed=True).exists()
        return False


class LevelSerializer(serializers.ModelSerializer):
    modules = ModuleSerializer(many=True, read_only=True)
    modules_count = serializers.SerializerMethodField()
    completed_count = serializers.SerializerMethodField()
    completion_pct = serializers.SerializerMethodField()

    class Meta:
        model = Level
        fields = ('id', 'slug', 'title', 'description', 'color', 'text_color', 'accent',
                  'order', 'icon', 'modules', 'modules_count', 'completed_count', 'completion_pct')

    def get_modules_count(self, obj):
        return obj.modules.count()

    def get_completed_count(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.modules.filter(completions__user=request.user, completions__completed=True).count()
        return 0

    def get_completion_pct(self, obj):
        total = obj.modules.count()
        if not total:
            return 0
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            done = obj.modules.filter(completions__user=request.user, completions__completed=True).count()
            return round(done / total * 100)
        return 0


class UserProgressSerializer(serializers.ModelSerializer):
    module_title = serializers.CharField(source='module.title', read_only=True)
    level_title = serializers.CharField(source='module.level.title', read_only=True)
    level_color = serializers.CharField(source='module.level.color', read_only=True)

    class Meta:
        model = UserProgress
        fields = ('id', 'module', 'module_title', 'level_title', 'level_color', 'completed', 'completed_at', 'notes')
