from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Level, Module, UserProgress, UserProfile
from .serializers import (
    RegisterSerializer, UserSerializer, LevelSerializer,
    ModuleSerializer, UserProgressSerializer
)


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = (permissions.AllowAny,)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user, context={'request': request}).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            },
            'message': 'Bienvenue sur PyLearn ! Ton compte est créé.'
        }, status=status.HTTP_201_CREATED)


class MeView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        return Response(UserSerializer(request.user, context={'request': request}).data)

    def patch(self, request):
        user = request.user
        for field in ('first_name', 'last_name'):
            if field in request.data:
                setattr(user, field, request.data[field])
        user.save()
        profile = user.profile
        if 'bio' in request.data:
            profile.bio = request.data['bio']
        if 'avatar_url' in request.data:
            profile.avatar_url = request.data['avatar_url']
        profile.save()
        return Response(UserSerializer(user, context={'request': request}).data)


class LevelListView(generics.ListAPIView):
    queryset = Level.objects.prefetch_related('modules__exercises').all()
    serializer_class = LevelSerializer
    permission_classes = (permissions.AllowAny,)

    def get_serializer_context(self):
        return {**super().get_serializer_context(), 'request': self.request}


class ModuleDetailView(generics.RetrieveAPIView):
    queryset = Module.objects.prefetch_related('exercises').select_related('level').all()
    serializer_class = ModuleSerializer
    permission_classes = (permissions.AllowAny,)

    def get_serializer_context(self):
        return {**super().get_serializer_context(), 'request': self.request}


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def toggle_module(request, module_id):
    try:
        module = Module.objects.get(id=module_id)
    except Module.DoesNotExist:
        return Response({'error': 'Module introuvable'}, status=404)

    progress, _ = UserProgress.objects.get_or_create(user=request.user, module=module)
    profile = request.user.profile

    if progress.completed:
        progress.completed = False
        progress.completed_at = None
        profile.xp_total = max(0, profile.xp_total - module.xp_reward)
    else:
        progress.completed = True
        progress.completed_at = timezone.now()
        profile.xp_total += module.xp_reward
        profile.last_activity = timezone.now().date()

    progress.save()
    profile.save()

    total = Module.objects.count()
    completed = request.user.progress.filter(completed=True).count()
    pct = round(completed / total * 100) if total else 0

    return Response({
        'completed': progress.completed,
        'xp_total': profile.xp_total,
        'level_badge': profile.level_badge,
        'total_modules': total,
        'completed_modules': completed,
        'global_pct': pct,
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def my_progress(request):
    progress_qs = UserProgress.objects.filter(
        user=request.user, completed=True
    ).select_related('module__level').order_by('-completed_at')

    total = Module.objects.count()
    completed = progress_qs.count()

    return Response({
        'progress': UserProgressSerializer(progress_qs, many=True).data,
        'stats': {
            'total': total,
            'completed': completed,
            'percentage': round(completed / total * 100) if total else 0,
            'xp': request.user.profile.xp_total,
            'badge': request.user.profile.level_badge,
        }
    })


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def public_stats(request):
    return Response({
        'total_users': User.objects.count(),
        'total_modules': Module.objects.count(),
        'total_completions': UserProgress.objects.filter(completed=True).count(),
        'levels_count': Level.objects.count(),
    })
