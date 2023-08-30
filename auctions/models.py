from django.contrib.auth.models import AbstractUser
from django.db import models
from decimal import *


class User(AbstractUser):
    pass
    watchlist = models.ManyToManyField('AuctionListing', related_name="watchers", null=True, blank=True)


class Category(models.Model):
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
    categories = models.ManyToManyField(Category, related_name="listings")

    def is_valid_price(self, price: Decimal) -> bool:
        bid_num =  self.bids.count()
        if bid_num > 0:
            won_bid = self.bids.order_by("-price").first()
            highest_bid = won_bid.price
            lowest_price = highest_bid + Decimal(0.01)
        else:
            highest_bid = self.starting_bid
            lowest_price = highest_bid
        lowest_price = round(lowest_price, 2)
        return price >= lowest_price


class Bid(models.Model):
    bid_maker = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")
    listing = models.ForeignKey(AuctionListing, on_delete=models.CASCADE, related_name="bids")
    price = models.DecimalField(decimal_places=2, max_digits=7)
