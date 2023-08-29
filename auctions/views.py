from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms
from .models import User, AuctionListing, Bid, Comment, Catagory

class ListingForm(forms.Form):
    catagory = Catagory.objects.exclude(name="Other").values('name', 'id')
    catagory_list = []
    for i in range(len(catagory)):
        catagory_list.append((catagory[i]['id'], catagory[i]['name']))
    catagory_list.append((Catagory.objects.get(name="Other").id, "Other"))
    title = forms.CharField(max_length=64)
    description = forms.CharField(max_length=500, widget=forms.Textarea)
    image = forms.ImageField(required=False)
    starting_bid = forms.DecimalField(decimal_places=2, max_digits=5)
    catagories = forms.MultipleChoiceField(choices=catagory_list)


@login_required
def index(request):

    listings = request.user.listings.all()
    new_listings = []
    for i in range(len(listings)):
        listing = listings[i]
        bid_num = listing.bids.count()
        if bid_num == 0:
            highest_bid = listing.starting_bid
        else:
            highest_bid = listing.bids.order_by("-price").first().price

        new_listings.append({
            "listing": listing,
            "highest_bid": highest_bid
        })
    return render(request, "auctions/index.html", {
        "listings": new_listings
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


@login_required
def create(request):
    if request.method == "GET":
        return render(request, "auctions/create.html", {
            "form": ListingForm()
        })
    if request.method == "POST":
        form = ListingForm(request.POST, request.FILES)
        if form.is_valid():
            title = form.cleaned_data['title']
            description = form.cleaned_data['description']
            image = form.cleaned_data['image']
            starting_bid = form.cleaned_data['starting_bid']
            listing = AuctionListing(owner=request.user, 
                                          title=title,
                                          description=description,
                                          image=image,
                                          starting_bid=starting_bid)
            listing.save()
            catagories = form.cleaned_data['catagories']
            for catagory_id in catagories:
                result = Catagory.objects.get(id=catagory_id)
                if result:
                    catagory = result
                    listing.catagories.add(catagory)
        return render(request, "auctions/create.html", {
            "form": ListingForm()
        })
    

def listing(request, id):
    if AuctionListing.objects.filter(id=id).exists():  
        listing = AuctionListing.objects.get(id=id)
        owner = listing.owner
        bid_num =  listing.bids.count()
        if bid_num > 0:
            highest_bid = listing.bids.order_by("-price").first().price
        else:
            highest_bid = listing.starting_bid
        return render(request, "auctions/listing.html", {
            "listing": listing,
            "highest_bid": highest_bid,
            "bid_num": bid_num,
            "owner": owner
        })
    return HttpResponseRedirect(reverse("index"))
        