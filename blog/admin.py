from django.contrib import admin
from .models import *
admin.site.register(MyUser)
admin.site.register(Post)
admin.site.register(CommentPost)
admin.site.register(LikePost)
admin.site.register(FollowMyUser)

# Register your models here.
