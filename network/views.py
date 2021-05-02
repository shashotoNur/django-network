import json
from django.core.paginator import Paginator
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse

from .models import User, Post, Follow, Like

#AnonymousUser
def index(request, post_id=0):
    user = request.user

    if request.method == "POST" and not user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))

    if request.method == "POST" and user.is_authenticated:
        if request.POST.get("post") is not None:
            body = request.POST.get("post")
            if body != "":
                Post.objects.create(user=user, body=body, likes=0)

        if post_id != 0:
            post = Post.objects.get(id=post_id)

            if json.loads(request.body).get('postBody') is not None and user == post.user:
                body = json.loads(request.body).get('postBody')
                if body != "":
                    post.body = body
                    post.save()

            elif json.loads(request.body).get('toggleLike') is not None and user != post.user:
                try:
                    like = Like.objects.get(user=user, post=post)
                    like.delete()
                except Like.DoesNotExist:
                    Like.objects.create(user=user, post=post)

                post.likes = Like.objects.filter(post=post).count()
                post.save()

                serialized_data = post.serialize()
                return JsonResponse(serialized_data)

    posts = Post.objects.all().order_by('-timestamp')
    if user.is_authenticated:
        for post in posts:
            liked = (Like.objects.filter(user=user, post=post).count() != 0)
            post = post.__dict__
            post['liked'] = liked
        

    page_number = request.GET.get('page', 1)
    paginated_posts = Paginator(posts, 10)
    post_page = paginated_posts.get_page(page_number)

    return render(request, "network/index.html", {
        "post_page": post_page
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
       
        return render(request, "network/register.html")


@login_required(login_url="login")
def following(request):
    user = request.user

    following = Follow.objects.filter(follower=user).values('following_id')
    posts = Post.objects.filter(user__in=following).order_by('-timestamp')

    post_dict = {}
    for post in posts:
        liked = (Like.objects.filter(user=user, post=post).count() != 0)
        post = post.__dict__
        post['liked'] = liked

    page_number = request.GET.get('page', 1)
    paginated_posts = Paginator(posts, 10)
    post_page = paginated_posts.get_page(page_number)

    return render(request, "network/following.html", {
        "post_page": post_page
    })


@login_required(login_url="login")
def profile(request, user_id):
    user = request.user
    other_user = User.objects.get(id=user_id)

    if request.method == "POST" and user != other_user:
        if request.POST["button"] == "Follow":
            button = "Unfollow"
            Follow.objects.create(follower=request.user, following=other_user)
        else:
            button = "Follow"
            Follow.objects.get(follower=request.user, following=other_user).delete()

    posts = Post.objects.filter(user=other_user.id).order_by('-timestamp')

    post_dict = {}
    for post in posts:
        liked = (Like.objects.filter(user=user, post=post).count() != 0)
        post = post.__dict__
        post['liked'] = liked

    page_number = request.GET.get('page', 1)
    paginated_post = Paginator(posts, 10)
    post_page = paginated_post.get_page(page_number)

    following = Follow.objects.filter(follower=request.user, following=other_user).count() == 0
    button = "Follow" if following else "Unfollow"

    return render(request, "network/profile.html", {
        "other_user": other_user, 
        "followers": Follow.objects.filter(following=other_user).count(), 
        "following": Follow.objects.filter(follower=other_user).count(), 
        "post_page": post_page, 
        "button": button
    })