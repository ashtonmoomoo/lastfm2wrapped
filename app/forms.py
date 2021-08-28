from django import forms

class YearAndUserNameForm(forms.Form):
    """Get a year and last.fm username from the user."""

    year = forms.IntegerField()
    username = forms.CharField()
    token = forms.CharField() ## Cheeky