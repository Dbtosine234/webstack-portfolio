from django.contrib import admin

# Register your models here.

from .models import Course, Topic, Message, User 
admin.site.register(User)
admin.site.register(Course)
admin.site.register(Topic)
admin.site.register(Message)
