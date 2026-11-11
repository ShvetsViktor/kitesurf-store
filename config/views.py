from django.shortcuts import render


def home(request):
    """Render the public homepage."""
    return render(request, 'home.html')
