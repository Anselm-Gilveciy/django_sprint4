from django import forms

from .models import Post, Comment


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        exclude = ('author',)
        widgets = {
            'text': forms.Textarea({'cols': '22', 'rows': '5'}),
            'pub_date': forms.DateTimeInput(
                attrs={'type': 'datetime-local', 'class': 'form'}
            )
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)