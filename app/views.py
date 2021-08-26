from django.shortcuts import render

def home(request):
    """Homepage is a completely static form."""
    return render(request, 'home.html')