from django.contrib import admin
from django.contrib.auth.models import Group, User
from .models import Profile, Meep

#unregister group
admin.site.unregister(Group)

#mix profile info into user info
class ProfileInline(admin.StackedInline):
    model = Profile

#extend user model
class UserAdmin(admin.ModelAdmin):
    model = User
    #display username fields on admin page
    fields = ["username"]
    inlines = [ProfileInline]

#unregister initial user
admin.site.unregister(User)

#reregister user
admin.site.register(User, UserAdmin)

#register meeps
admin.site.register(Meep)
