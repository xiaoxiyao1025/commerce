from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    content = models.CharField(max_length=140)

class AuctionListing(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings")
    title = models.CharField(max_length=64)
    description = models.CharField(max_length=500)
    image = models.ImageField(width_field=500, height_field=400, null=True)
    comments = models.ManyToManyField(Comment, related_name="listing")
    starting_bid = models.DecimalField(decimal_places=2, max_digits=6)
    active = models.BooleanField()

class Bid(models.Model):
    bid_maker = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")
    listing = models.ForeignKey(AuctionListing, on_delete=models.CASCADE, related_name="bids")
    price = models.DecimalField(decimal_places=2, max_digits=7)
    