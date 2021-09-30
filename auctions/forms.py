from django import forms
from . import models

class CreateForm(forms.Form):
    title = forms.CharField(label='Listing title', max_length=100)
    description = forms.CharField(label='Listing description', widget=forms.Textarea)
    starting_bid = forms.FloatField(label='Starting bid')
    image_url = forms.URLField(label='Image URL', required = False)
    category = forms.ChoiceField(choices=models.Listing.CATEGORY_CHOICES)

class BidForm(forms.Form):
    price = forms.FloatField(label = '', min_value=0, widget=forms.NumberInput(attrs={'placeholder': 'Bid'}))

class CommentForm(forms.Form):
    comment = forms.CharField(widget = forms.Textarea(attrs = {'placeholder': 'Your comment', 'style': 'height: 100px; width:500px'}), label='')