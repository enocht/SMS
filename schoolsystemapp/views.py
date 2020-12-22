from django.shortcuts import render


# Create your views here.
def index(request):
    page_title = "Utron - Welcome Page"
    return render(request, "index.html", {'page_title': page_title})
