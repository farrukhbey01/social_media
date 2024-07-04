from django.urls import path
from .views import (login_view, home, logout_view,register_view, upload_view,follow,like,
                    profile_view,profile_upload_view,test_sql,search_view,comments_view,setting_view,delete_post_view)

urlpatterns = [
    path('',home),
    path('login/', login_view),
    path('logout/',logout_view),
    path('register/',register_view),
    path('upload/',upload_view),
    path('profile/', profile_view),
    path('upload_profile/',profile_upload_view),
    path('search/', search_view),
    path('delete_post/', delete_post_view),
    path('follow/',follow),
    path('like/',like),
    path('profile_info/', profile_view),
    path('setting/', setting_view),
    path('post/<int:post_id>/comments/', comments_view),
    path('test_sql/',test_sql)


]