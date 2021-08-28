from django import forms
from datetime import date

class YearAndUserNameForm(forms.Form):
    """Get a year and last.fm username from the user."""

    years_since_lastfm_started = tuple([(str(year), str(year)) for year in range(date.today().year, 2002, -1)])

    year = forms.ChoiceField(choices=years_since_lastfm_started)
    username = forms.CharField()
    is_own = forms.BooleanField(required=False)
    token = forms.CharField(widget=forms.HiddenInput()) ## Cheeky