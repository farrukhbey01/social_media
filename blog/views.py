from django.contrib.auth.hashers import make_password
from django.http import HttpResponse
from django.shortcuts import render, redirect
from .models import *
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout


def function(post, comments):
    post.comments = comments.filter(post_id=post.id)
    post.likes = LikePost.objects.filter(post_id=post.id).order_by('created_at')[:3]
    post.last_liked = post.likes.first()
    return post


@login_required(login_url='/login/')
def home(request):
    my_user = MyUser.objects.filter(user=request.user).first()
    followed_users = FollowMyUser.objects.filter(follower=my_user).values_list('following', flat=True)
    users = MyUser.objects.exclude(user=request.user)
    display_users = users.exclude(id__in=followed_users)
    # posts = map(lambda post: func(post, CommentPost.objects.all()), Post.objects.filter(author__in=followed_users))

    posts = Post.objects.filter(Q(author__in=followed_users) | Q(author=my_user)).distinct()
    posts = map(lambda post: function(post, CommentPost.objects.all()), posts)
    d = {
        'posts': posts,
        'user': MyUser.objects.filter(user=request.user).first(),
        'profiles': MyUser.objects.all().exclude(user=request.user),
        'users': display_users[:3]
    }
    if request.method == 'POST':
        data = request.POST
        message = data['message']
        post_id = data['post_id']
        my_user = MyUser.objects.filter(user=request.user).first()
        comment_post = Post.objects.filter(pk=post_id).first()
        obj = CommentPost.objects.create(message=message, post_id=post_id, author=my_user)
        obj.save()
        obj = CommentPost.objects.create(author=my_user, post_id=post_id)
        obj.save()
        comment_post.comment_count += 1
        comment_post.save(update_fields=['comment_count'])
        return redirect('/#{}'.format(post_id))
    return render(request, 'index.html', context=d)


@login_required(login_url='/auth/login/')
def comments_view(request, post_id):
    post = Post.objects.filter(pk=post_id).first()
    comments = CommentPost.objects.filter(post=post).all()
    return render(request, 'index.html', context={'post': post, 'comments': comments})


def login_view(request):
    d = {}

    if request.method == 'POST':
        data = request.POST
        username = data['username']
        password = data['password']
        d['error'] = f'user {username} username not found'
        user = authenticate(username=username, password=password)
        print(user)
        if user:
            login(request, user)
            return redirect('/')

        else:
            d['error'] = 'user not found'

    return render(request, 'signin.html', context=d)


@login_required(login_url='/login')
def logout_view(request):
    logout(request)
    return redirect('/login')


def register_view(request):
    d = {}
    if request.method == 'POST':
        data = request.POST
        username = data['username']
        p1 = data['password1']
        p2 = data['password2']
        if not User.objects.filter(username=username).exists() and p1 == p2:
            user = User.objects.create(username=username, password=make_password(p1))
            user.save()
            profile = MyUser.objects.create(username=username, user=user)
            profile.save()
            return redirect('/login')
        d['error'] = "Username is already taken or passwords don't match"
    return render(request, 'signup.html', context=d)


@login_required(login_url='/auth/login/')
def setting_view(request):
    return render(request, 'setting.html')


def upload_view(request):
    if request.method == 'POST':
        my_user = MyUser.objects.filter(username=request.user).first()
        my_user.post_count += 1
        my_user.save(update_fields=['post_count'])
        post = Post.objects.create(image=request.FILES['image'], author=my_user)
        post.save()
        return redirect('/')
    return redirect('/')


def profile_upload_view(request):
    if request.method == 'POST':
        my_user = MyUser.objects.filter(username=request.user).first()
        my_user.image = request.FILES['image']
        my_user.save(update_fields=['image'])
        return redirect('/profile/')
    return redirect('/profile/')


def follow(request):
    profile_id = request.GET.get('profile_id')
    my_user = MyUser.objects.filter(username=request.user).first()
    profile = MyUser.objects.filter(id=profile_id).first()
    follow_exists = FollowMyUser.objects.filter(follower=my_user, following_id=profile_id)
    if follow_exists.exists():
        follow_exists.delete()
        profile.follower_count -= 1
        profile.save(update_fields=['follower_count'])
    else:
        obj = FollowMyUser.objects.create(follower=my_user, following_id=profile_id)
        obj.save()
        profile.follower_count += 1
        profile.save(update_fields=['follower_count'])
    if 'redirect' in request.GET:
        return redirect(f'/profile_info?profile_id={profile_id}')
    return redirect('/')


def like(request):
    post_id = request.GET.get('post_id')
    my_user = MyUser.objects.filter(username=request.user).first()
    post = Post.objects.filter(id=post_id).first()
    like_exists = LikePost.objects.filter(author=my_user, post_id=post_id)
    if like_exists.exists():
        like_exists.delete()
        post.like_count -= 1
        post.save(update_fields=['like_count'])
    else:
        obj = LikePost.objects.create(author=my_user, post_id=post_id)
        obj.save()
        post.like_count += 1
        post.save(update_fields=['like_count'])

    return redirect('/')


@login_required(login_url='/auth/login/')
def profile_view(request):
    if 'profile_id' in request.GET:
        profile_id = request.GET.get('profile_id')
        profile = MyUser.objects.filter(pk=profile_id).first()
    elif 'author_id' in request.GET:
        profile_id = request.GET.get('author_id')
        profile = MyUser.objects.filter(pk=profile_id).first()
    else:
        profile = MyUser.objects.filter(user=request.user).first()
    followers_count = profile.follower_count
    followings_count = profile.following_count
    posts_count = profile.post_count
    profile_pic = profile.image
    bio = profile.bio
    user_posts = Post.objects.filter(author=profile)
    d = {
        'profile_pic': profile_pic,
        'bio': bio,
        'profile': profile,
        'user': MyUser.objects.filter(user=request.user).first(),
        'followers': followers_count,
        'followings': followings_count,
        'posts': posts_count,
        'user_posts': user_posts,
    }
    return render(request, 'profile.html', context=d)


@login_required(login_url='/auth/login/')
def search_view(request):
    if request.method == 'POST':
        query = request.POST.get('query')
        return redirect(f'/search?u={query}')
    query = request.GET.get('u')
    usernames = MyUser.objects.filter(user__username__icontains=query)
    if query is not None and len(query) >= 1:
        posts = Post.objects.all()
        usernames = MyUser.objects.filter(user__username__icontains=query)
        return render(request, 'index.html', {'usernames': usernames, 'posts': posts,
                                              'user': MyUser.objects.filter(user=request.user).first(),
                                              'profiles': MyUser.objects.all().exclude(user=request.user), })

    if query != usernames:
        return render(request, 'index.html', {'usernames': usernames})


@login_required(login_url='/auth/login/')
def delete_post_view(request):
    data = request.GET
    post_id = data.get("post_id")
    post = Post.objects.filter(pk=post_id).first()
    if post.author.user == request.user:
        my_user = MyUser.objects.filter(user=request.user).first()
        my_user.post_count -= 1
        my_user.save(update_fields=['post_count'])

        post.delete()
        latest_post = Post.objects.last()
        return redirect('/#{}'.format(latest_post.id))
    return render(request, 'error.html')


# Create your views here.

def test_sql(request):
    query = """CREATE TABLE contact
    ( id bigserial primary key, 
    name varchar(125), 
    message text, 
    created_at timestamp default CURRENT_TIMESTAMP);"""

    Post.objects.raw(query)

    return HttpResponse('ok')
