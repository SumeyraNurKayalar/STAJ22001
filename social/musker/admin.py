from django.contrib import admin
from django.urls import path
from django.shortcuts import render
from django.contrib.auth.models import Group, User
from .models import Profile, Meep, MeepReport, AdminNotification


class CustomAdminSite(admin.AdminSite):
    site_header = 'Meep Management Panel' 
    site_title = 'Meep Admin'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('notification-dashboard/', self.admin_view(self.notification_dashboard), 
                 name='notification_dashboard'),
        ]
        return custom_urls + urls
    
    def notification_dashboard(self, request):
        unread_notifications = AdminNotification.objects.filter(is_read=False).order_by('-created_at')
        recent_notifications = AdminNotification.objects.all().order_by('-created_at')[:10]
        report_count = MeepReport.objects.count()

        context = {
            'unread_notifications': unread_notifications,
            'recent_notifications': recent_notifications,
            'report_count': report_count,
            'title': 'Notification Management',
            **self.each_context(request),
        }
        return render(request, 'admin/notification_dashboard.html', context)


# works for unregistering, only creates custom_admin_site
custom_admin_site = CustomAdminSite(name='custom_admin')

#mix profile info into user info
class ProfileInline(admin.StackedInline):
    model = Profile

#extend user model
class UserAdmin(admin.ModelAdmin):
    model = User
    fields = ["username"]
    inlines = [ProfileInline]


@admin.register(MeepReport)
class MeepReportAdmin(admin.ModelAdmin):
    list_display = ("meep", "reported_by", "reason", "created_at")
    list_filter = ("created_at",)
    search_fields = ("meep__body", "reported_by__username")

    actions = ['delete_reports', 'delete_reports_and_meep']

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def delete_reports(self, request, queryset):
        count = queryset.count()
        queryset.delete()
        self.message_user(request, f"{count} report(s) successfully deleted.")
    delete_reports.short_description = "Delete selected reports"

    def delete_reports_and_meep(self, request, queryset):
        count = 0
        for report in queryset:
            report.meep.delete()
            count += 1
        queryset.delete()
        self.message_user(request, f"{count} meep(s) and their reports deleted.")
    delete_reports_and_meep.short_description = "Delete selected meeps and the report"


#unregister initial user
admin.site.unregister(User)

#reregister user
admin.site.register(User, UserAdmin)

#register meeps
admin.site.register(Meep)

@admin.register(AdminNotification)
class AdminNotificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'notification_type', 'is_read', 'created_at', 'short_message']
    list_filter = ['is_read', 'notification_type', 'created_at']
    search_fields = ['title', 'message']
    readonly_fields = ['created_at']
    list_editable = ['is_read']
    
    #show the shorter version of the message
    def short_message(self, obj):
        return obj.message[:50] + '...' if len(obj.message) > 50 else obj.message
    short_message.short_description = 'Message'

    actions = ['mark_as_read', 'mark_as_unread', 'delete_notifications']

    def mark_as_read(self, request, queryset):
        updated_count = queryset.update(is_read=True)
        self.message_user(request, f"{updated_count} notification marked as read.")
    mark_as_read.short_description = "Mark selected notifications as read"

    def mark_as_unread(self, request, queryset):
        updated_count = queryset.update(is_read=False)
        self.message_user(request, f"{updated_count} notification marked as unread.")
    mark_as_unread.short_description = "Mark selected notifications as unread"

    def delete_notifications(self, request, queryset):
        deleted_count = queryset.count()
        queryset.delete()
        self.message_user(request, f"{deleted_count} notification deleted.")
    delete_notifications.short_description = "Delete the marked notifications"
