from .models import AdminNotification

def notifications(request):
    context = {}
    if request.user.is_authenticated and request.user.is_staff:
        context['notifications'] = AdminNotification.objects.all().order_by('-created_at')[:5]
        context['unread_notifications_count'] = AdminNotification.objects.filter(is_read=False).count()
    return context