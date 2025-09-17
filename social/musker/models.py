from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_save
from django.dispatch import receiver
import datetime


#create meep model
class Meep(models.Model):
    user = models.ForeignKey(User, related_name="meeps", on_delete=models.DO_NOTHING)
    body = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, related_query_name="meep_like", blank=True)

    #keep track and count of likes
    def number_of_likes(self):
        return self.likes.count()

    def __str__(self):
        return(f"{self.user}"
               f"({self.created_at:%Y-%m-%d %H.%M: }):"
               f"{self.body} "
        )
    
class MeepReport(models.Model):
    meep = models.ForeignKey("Meep", on_delete=models.CASCADE, related_name="reports")
    reported_by = models.ForeignKey(User, on_delete=models.CASCADE)
    reason = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.meep} reported by {self.reported_by}"

# Create user profile models here.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    follows = models.ManyToManyField("self", 
                                     related_name="followed_by",
                                     symmetrical=False,
                                     blank=True)

    date_modified = models.DateTimeField(auto_now=True)
    profile_image = models.ImageField(null = True, blank = True, upload_to="images/")
   
    profile_bio = models.CharField(null=True, blank=True, max_length=500)
    homepage_link = models.CharField(null=True, blank=True, max_length=100)
    facebook_link = models.CharField(null=True, blank=True, max_length=100)
    instagram_link =models.CharField(null=True, blank=True, max_length=100)
    linkedin_link = models.CharField(null=True, blank=True, max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username
    
#comment on other meeps    
class Comment(models.Model):
    meep = models.ForeignKey(Meep, related_name="comments", on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user} on {self.meep}"
   
    
#create profile when new user signs up
def create_profile(sender, instance, created, **kwargs):
    if created:
        user_profile = Profile(user = instance)
        user_profile.save()

        #make the user follow themselves
        user_profile.follows.set([instance.profile.id])
        user_profile.save()

post_save.connect(create_profile, sender=User)

class AdminNotification(models.Model):
    NOTIFICATION_TYPES = (
        ('report', 'REPORTS'),
        ('user', 'USER INFORMATION'),
        ('system', 'SYSTEM INFORMATION'),
    )

    title = models.CharField(max_length=200, verbose_name="Title")
    message = models.TextField(verbose_name="Message")
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='report')
    is_read = models.BooleanField(default=False, verbose_name="Read")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created time")
    related_object_id = models.PositiveBigIntegerField(null=True, blank=True)
    
    #usng a Charfield here
    content_type = models.CharField(max_length=50, null=True, blank=True, verbose_name="Content Type")

    class Meta:
        verbose_name = "Administrator Notice"
        verbose_name_plural = "Administrator Notices"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.created_at.strftime('%d.%m.%Y %H:%M')}"
