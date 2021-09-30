from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Listing(models.Model):
    title = models.CharField(max_length=64)    
    description = models.CharField(max_length=500)
    image_url = models.URLField(blank=True)

    NO_CATEGORY = 'NO'
    FASHION = 'FS'
    TOYS = 'TY'
    ELECTRONICS = 'EL'
    HOME = 'HM'
    MAGIC_THINGS = 'MG'
    SPORT = 'SP'
    CATEGORY_CHOICES = [
        (NO_CATEGORY, 'No category'), (FASHION, 'Fashion'), (TOYS, 'Toys'), (ELECTRONICS, 'Electronics'), 
        (HOME, 'Home'), (MAGIC_THINGS, 'Magic things'), (SPORT, "Sport")
    ]
    category = models.CharField(max_length=2, choices=CATEGORY_CHOICES, default=NO_CATEGORY)

    current_price = models.FloatField(default=0)

    date_of_creating = models.DateTimeField(auto_created=True, default="2000-01-01 00:00")

    is_active = models.BooleanField(default=True)

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings")
    def __str__(self):
        return f"{self.title}"

    def price(self):
        return self.bids[-1].price

class Bid(models.Model):
    price = models.FloatField(default=0)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bids")
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")
    def __str__(self):
        return f"{self.price}"

class Comment(models.Model):
    text = models.CharField(max_length=500)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comments")

    def __str__(self):
        return f"{self.text}"

class WatchList(models.Model):
    owner = models.OneToOneField(User, on_delete=models.CASCADE, related_name="watchlist")
    listings = models.ManyToManyField(Listing, related_name="watchlists")