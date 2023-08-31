from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms
from .models import User, AuctionListing, Bid, Comment, Category
from decimal import *
from .helper import get_listing_set, reverse_with_message

class ListingForm(forms.Form):
    category = Category.objects.exclude(name="Other").values('name', 'id')
    category_list = []
    for i in range(len(category)):
        category_list.append((category[i]['id'], category[i]['name']))
    category_list.append((Category.objects.get(name="Other").id, "Other"))
    title = forms.CharField(max_length=64)
    description = forms.CharField(max_length=500, widget=forms.Textarea)
    image = forms.ImageField(required=False)
    starting_bid = forms.DecimalField(decimal_places=2, max_digits=5)
    categories = forms.MultipleChoiceField(choices=category_list)

class CloseListingForm(forms.Form):
    listing_id = forms.CharField(widget=forms.HiddenInput())

class BidForm(forms.Form):
    listing_id = forms.CharField(widget=forms.HiddenInput())
    price = forms.DecimalField()

class CommentForm(forms.Form):
    listing_id = forms.CharField(widget=forms.HiddenInput())
    content = forms.CharField(label="Comment", max_length=140)

class WatchlistForm(forms.Form):
    listing_id = forms.CharField(widget=forms.HiddenInput())

@login_required
def index(request):
    message = request.GET.get("message")
    # get the all user's listing
    listings = request.user.listings.all()
    new_listings = get_listing_set(listings)
    return render(request, "auctions/index.html", {
        "listings": new_listings,
        "message": message
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
            # save the listing without categories
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

            # add cat
            categories = form.cleaned_data['categories']
            for category_id in categories:
                result = Category.objects.get(id=category_id)
                if result:
                    category = result
                    listing.categories.add(category)
        else:
            return render(request, "auctions/create.html", {
            "form": form
        })
        return render(request, "auctions/create.html", {
            "form": ListingForm()
        })
    

def listing(request, id):
    if AuctionListing.objects.filter(id=id).exists():  
        listing = AuctionListing.objects.get(id=id)
        owner = listing.owner
        bid_num =  listing.bids.count()
        if bid_num > 0:
            won_bid = listing.bids.order_by("-price").first()
            highest_bid = won_bid.price
            won_user = won_bid.bid_maker
            lowest_price = highest_bid + Decimal(0.01)
        else:
            won_user = None
            highest_bid = listing.starting_bid
            lowest_price = highest_bid

        # check if the user who browse the website is owner or winner
        watchlist_form = None
        is_watched = False
        close_form = None
        comment_form = None
        bid_form = None
        is_winner = False
        if request.user.is_authenticated:
            # signed in
            comment_form = CommentForm(initial={"listing_id": listing.id})

            # check if the listing is in the user's watchlist
            watchlist_form = WatchlistForm(initial={"listing_id": listing.id})
            if request.user.watchlist.filter(id=listing.id).exists():
                is_watched = True

            # signed in, owner, active
            if request.user == owner and listing.active:
                close_form = CloseListingForm(initial={"listing_id": listing.id})
            
            else:
                # signed in, not owner, active
                if listing.active:
                    bid_form = BidForm(initial={
                        "listing_id": listing.id
                    })
                    bid_form.fields["price"].widget.attrs['min'] = lowest_price
                
                # signed in, not owner, not active, winner
                elif won_user == request.user:
                    is_winner = True
            
        return render(request, "auctions/listing.html", {
            "listing": listing,
            "highest_bid": highest_bid,
            "bid_num": bid_num,
            "owner": owner,
            "close_form": close_form,
            "comment_form": comment_form,
            "bid_form": bid_form,
            "is_winner": is_winner,
            "watchlist_form": watchlist_form,
            "is_watched": is_watched
        })
    # error page here
    # not found
    return HttpResponseRedirect(reverse("index"))
        

def close(request):
    if request.method == "GET":
        return HttpResponseRedirect(reverse("index"))
    # POST 
    form = CloseListingForm(request.POST)
    if form.is_valid():
        listing_id = form.cleaned_data["listing_id"]
        if AuctionListing.objects.filter(id = listing_id).exists():
            # listing exist

            listing = AuctionListing.objects.get(id = listing_id)

            owner = listing.owner
            if owner == request.user:
                # id ok, is owner
                listing.active = False
                listing.save()

        return HttpResponseRedirect(reverse("listing", kwargs={"id": listing_id}))
    # error page here
    # form invalid
    return HttpResponseRedirect(reverse("index"))


@login_required
def comment(request):
    if request.method == "GET":
        return HttpResponseRedirect(reverse("index"))
    # POST 
    form = CommentForm(request.POST)
    if form.is_valid():
        listing_id = form.cleaned_data["listing_id"]
        if AuctionListing.objects.filter(id = listing_id).exists():
            # listing exist

            listing = AuctionListing.objects.get(id = listing_id)

            comment = Comment(author=request.user, content=form.cleaned_data["content"])
            comment.save()
            listing.comments.add(comment)
                
        return HttpResponseRedirect(reverse("listing", kwargs={"id": listing_id}))
    # error page here
    # form invalid
    return HttpResponseRedirect(reverse("index"))


@login_required
def bid(request):
    if request.method == "GET":
        return HttpResponseRedirect(reverse("index"))
    # POST 
    form = BidForm(request.POST)
    if form.is_valid():
        listing_id = form.cleaned_data["listing_id"]
        print("valid")
        if AuctionListing.objects.filter(id = listing_id).exists():
            # listing exist
            print("exist")
            listing = AuctionListing.objects.get(id = listing_id)
            price = form.cleaned_data["price"]

            # check if listing is active and price is valid for the bid
            if listing.active and listing.is_valid_price(price):
                print("active and valid price")
                # add bid
                bid = Bid(bid_maker=request.user, listing=listing, price=price)
                bid.save()

        return HttpResponseRedirect(reverse("listing", kwargs={"id": listing_id}))
    # print(form.errors)
    # error page here
    # form invalid
    return HttpResponseRedirect(reverse("index"))


@login_required
def watchlist(request):
    if request.method == "GET":
        watchlist = request.user.watchlist.all()
        new_watchlist = get_listing_set(watchlist)
        return render(request, "auctions/watchlist.html", {
            "watchlist": new_watchlist
        })
    # POST 
    form = CloseListingForm(request.POST)
    if form.is_valid():
        listing_id = form.cleaned_data["listing_id"]
        if AuctionListing.objects.filter(id = listing_id).exists():
            # listing exist

            listing = AuctionListing.objects.get(id = listing_id)
            if request.user.watchlist.contains(listing):
                request.user.watchlist.remove(listing)
            else:
                request.user.watchlist.add(listing)

        return HttpResponseRedirect(reverse("listing", kwargs={"id": listing_id}))
    # error page here
    # form invalid
    return HttpResponseRedirect(reverse("index"))


