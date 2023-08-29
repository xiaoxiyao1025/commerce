from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Catagory(models.Model):
    name = models.CharField(max_length=64)

class Comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    content = models.CharField(max_length=140)

class AuctionListing(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings")
    title = models.CharField(max_length=64)
    description = models.CharField(max_length=500)
    image = models.ImageField(upload_to="auctions", null=True, blank=True)
    comments = models.ManyToManyField(Comment, related_name="listing", null=True, blank=True)
    starting_bid = models.DecimalField(decimal_places=2, max_digits=6)
    active = models.BooleanField(default=True)
    catagories = models.ManyToManyField(Catagory, related_name="listings")

class Bid(models.Model):
    bid_maker = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")
    listing = models.ForeignKey(AuctionListing, on_delete=models.CASCADE, related_name="bids")
    price = models.DecimalField(decimal_places=2, max_digits=7)
    
