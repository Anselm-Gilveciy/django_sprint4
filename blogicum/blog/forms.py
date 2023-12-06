from django import forms

from .models import Comment, Post, User


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        exclude = ('author',)
        widgets = {
            'text': forms.Textarea({'cols': '22', 'rows': '5'}),
            'pub_date': forms.DateTimeInput(
                format='%d %B %Y, %H:%M',
                attrs={'type': 'datetime-local', 'class': 'form'},
            )
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)


class UserCreateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'username',
            'email'
        )
