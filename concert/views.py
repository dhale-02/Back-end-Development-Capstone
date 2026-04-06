from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.contrib.auth.hashers import make_password

from concert.forms import LoginForm, SignUpForm
from concert.models import Concert, ConcertAttending
import requests as req
import os


def signup(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = User.objects.create(username=username, password=make_password(password))
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
    else:
        form = SignUpForm()
    return render(request, "signup.html", {"form": form})


def index(request):
    return render(request, "index.html")


def songs(request):
    songs_url = os.environ.get("SONGS_URL", "http://localhost:5000")
    try:
        response = req.get(f"{songs_url}/song")
        songs_list = response.json()
    except Exception:
        songs_list = []
    return render(request, "songs.html", {"songs": songs_list})


def photos(request):
    photos_url = os.environ.get("PHOTOS_URL", "http://localhost:5001")
    try:
        response = req.get(f"{photos_url}/picture")
        photos_list = response.json()
    except Exception:
        photos_list = []
    return render(request, "photos.html", {"photos": photos_list})


def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return HttpResponseRedirect(reverse("index"))
    else:
        form = LoginForm()
    return render(request, "login.html", {"form": form})


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def concerts(request):
    concert_list = Concert.objects.all()
    return render(request, "concerts.html", {"concerts": concert_list})


def concert_detail(request, id):
    if request.user.is_authenticated:
        obj = Concert.objects.get(pk=id)
        try:
            status = obj.attendee.filter(user=request.user).first().attending
        except Exception:
            status = "-"
        return render(request, "concert_detail.html", {
            "concert_details": obj,
            "status": status,
            "attending_choices": ConcertAttending.AttendingChoices.choices
        })
    else:
        return HttpResponseRedirect(reverse("login"))


def concert_attendee(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            concert_id = request.POST.get("concert_id")
            attendee_status = request.POST.get("attendee_choice")
            concert_attendee_object = ConcertAttending.objects.filter(
                concert_id=concert_id, user=request.user).first()
            if concert_attendee_object:
                concert_attendee_object.attending = attendee_status
                concert_attendee_object.save()
            else:
                ConcertAttending.objects.create(
                    concert_id=concert_id,
                    user=request.user,
                    attending=attendee_status
                )
        return HttpResponseRedirect(reverse("concerts"))
    else:
        return HttpResponseRedirect(reverse("index"))
