from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Post, Comment, Profile


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['content', 'image']
        widgets = {
            'content': forms.Textarea(attrs={
                'placeholder': "What's blooming in your world today?",
                'rows': 3,
                'class': 'post-textarea',
            }),
            'image': forms.ClearableFileInput(attrs={
                'class': 'image-input',
                'accept': 'image/*',
            }),
        }
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.TextInput(attrs={
                'placeholder': 'Write a lovely comment...',
                'class': 'comment-input',
            }),
        }
class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']

        if commit:
            user.save()

        return user

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['bio', 'profile_picture']

        widgets = {
            'bio': forms.Textarea(attrs={
                'placeholder': 'Tell us a little about yourself...',
                'rows': 4,
                'class': 'profile-bio-input'
            }),
            'profile_picture': forms.ClearableFileInput(attrs={
                'class': 'profile-picture-input',
                'accept': 'image/*'
            })
        }

