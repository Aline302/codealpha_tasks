from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.contrib.auth.models import User
from .models import Post, Like, Comment, Profile, Follow
from .forms import PostForm, CommentForm, RegisterForm, ProfileForm
from django.db.models import Q

def home(request):
    posts = Post.objects.select_related('author').all()
    form = PostForm()

    return render(request, 'social/home.html', {
        'posts': posts,
        'form': form,
    })


@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)

        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()

            messages.success(request, 'Your post has bloomed! 🌸')
            return redirect('home')

        posts = Post.objects.select_related('author').all()
        return render(request, 'social/home.html', {
            'posts': posts,
            'form': form,
        })

    return redirect('home')
@login_required
@require_POST
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    like, created = Like.objects.get_or_create(
        user=request.user,
        post=post
    )

    if not created:
        like.delete()

    return redirect('home')
@login_required
@require_POST
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST)

    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()

        messages.success(request, 'Comment added successfully! 🌸')

    return redirect('home')
def register(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = RegisterForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(
                request,
                'Welcome to BLOOM! 🌸'
            )
            return redirect('home')
    else:
        form = RegisterForm()

    return render(request, 'social/register.html', {
        'form': form
    })
def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    error = None

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)
            messages.success(request, 'Welcome back to BLOOM! 🌸')
            return redirect('home')
        else:
            error = 'Invalid username or password.'

    return render(request, 'social/login.html', {
        'error': error
    })
@login_required
@require_POST
def logout_view(request):
    logout(request)
    messages.success(request, 'See you soon on BLOOM! 🌸')
    return redirect('login')

@login_required
def my_profile(request):
    profile, created = Profile.objects.get_or_create(
        user=request.user
    )

    posts = Post.objects.filter(
        author=request.user
    ).order_by('-created_at')

    posts_count = posts.count()

    followers_count = request.user.followers.count()
    following_count = request.user.following.count()

    context = {
        'profile': profile,
        'posts': posts,
        'posts_count': posts_count,
        'followers_count': followers_count,
        'following_count': following_count,
    }

    return render(request, 'social/profile.html', context)

@login_required
def edit_profile(request):
    profile, created = Profile.objects.get_or_create(
        user=request.user
    )

    if request.method == 'POST':
        form = ProfileForm(
            request.POST,
            request.FILES,
            instance=profile
        )

        if form.is_valid():
            form.save()
            messages.success(
                request,
                'Your profile has been updated! 🌸'
            )
            return redirect('my_profile')

    else:
        form = ProfileForm(instance=profile)

    return render(request, 'social/edit_profile.html', {
        'form': form,
        'profile': profile
    })


def user_profile(request, username):
    profile_user = get_object_or_404(User, username=username)

    if request.user.is_authenticated and request.user == profile_user:
        return redirect('my_profile')

    profile, created = Profile.objects.get_or_create(user=profile_user)

    posts = Post.objects.filter(
        author=profile_user
    ).order_by('-created_at')

    is_following = False

    if request.user.is_authenticated:
        is_following = Follow.objects.filter(
            follower=request.user,
            following=profile_user
        ).exists()

    context = {
        'profile_user': profile_user,
        'profile': profile,
        'posts': posts,
        'posts_count': posts.count(),
        'followers_count': Follow.objects.filter(
            following=profile_user
        ).count(),
        'following_count': Follow.objects.filter(
            follower=profile_user
        ).count(),
        'is_following': is_following,
    }

    return render(request, 'social/user_profile.html', context)


@login_required
@require_POST
def toggle_follow(request, username):
    profile_user = get_object_or_404(User, username=username)

    if request.user == profile_user:
        messages.error(request, "You cannot follow yourself.")
        return redirect('my_profile')

    follow, created = Follow.objects.get_or_create(
        follower=request.user,
        following=profile_user
    )

    if not created:
        follow.delete()
        messages.success(request, "You unfollowed this user.")
    else:
        messages.success(request, "You are now following this user! 🌸")

    return redirect('user_profile', username=username)

def explore(request):
    query = request.GET.get('q', '').strip()

    users = User.objects.all().order_by('username')

    if request.user.is_authenticated:
        users = users.exclude(id=request.user.id)

    if query:
        users = users.filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query)
        )

    users = users[:30]

    return render(request, 'social/explore.html', {
        'users': users,
        'query': query
    })
