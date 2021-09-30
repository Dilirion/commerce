from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from datetime import datetime


from .models import Listing, User, Bid, WatchList, Comment
from .forms import CreateForm, BidForm, CommentForm

def index(request):
    return render(request, "auctions/index.html", {
        'listings': Listing.objects.exclude(is_active = False).all(),
        'title': "Active listings"
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
            whatchlist = WatchList()
            whatchlist.owner = user
            whatchlist.save()
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
    if request.method == 'POST':
        form = CreateForm(request.POST)
        if form.is_valid():            
            listing = Listing(title = form.cleaned_data['title'], description = form.cleaned_data['description'],
                 image_url = form.cleaned_data['image_url'], category = form.cleaned_data['category'],
                 owner = request.user, date_of_creating = datetime.now(), current_price = form.cleaned_data['starting_bid'])                     
            listing.save()
            request.user.listings.add(listing)
            return HttpResponseRedirect(reverse("listing", args=[listing.id]))
    else:
        form = CreateForm()

    return render(request, 'auctions/create.html', {'form': form})

def listing(request, listing_id):
    try:
        listing = Listing.objects.get(pk = listing_id)
    except Listing.DoesNotExist:
        raise Http404("Listing not found.")
    
    message = None

    if request.method == 'POST' and 'bid_form' in request.POST:
        bid_form = BidForm(request.POST)
        if bid_form.is_valid():
            if bid_form.cleaned_data['price'] > listing.current_price or (listing.bids.count() == 0 and (bid_form.cleaned_data['price'] == listing.current_price)):
                bid = Bid(price = bid_form.cleaned_data['price'], bidder = request.user, listing = listing)
                bid.save()
                listing.current_price = bid.price
                listing.bids.add(bid)
                listing.save()
                bid_form = BidForm()
            elif listing.bids.count() == 0:
                message = "The price should be not less than current" 
            else:
                message = "The price should be greater than current"       
    else:
        bid_form = BidForm()
    
    if request.method == 'POST'and 'comment_form' in request.POST:
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = Comment(text = comment_form.cleaned_data['comment'], author = request.user, listing = listing)
            comment.save()
            listing.comments.add(comment)
            comment_form = CommentForm()
    else:
        comment_form = CommentForm()
    
    in_watchlist = False
    is_owner = False
    is_winner = False
    label = f"{listing.bids.count()} bids so far. "

    if request.user.is_authenticated:
        if listing in request.user.watchlist.listings.all():
            in_watchlist = True

        if listing.owner.id == request.user.id:
            is_owner = True

        if listing.bids.count()>0 and listing.bids.latest('id').bidder.id == request.user.id and listing.is_active == False:
            is_winner = True

        if listing.bids.count() > 0:
            if (listing.bids.latest('id')).bidder.id == request.user.id:
                label += "Your bid is the current bid."
            else:
                label += "Your bid must be greater than current price."
        else:
            label = "You will be the first bidder. Your bid must be not less than current price."

    return render(request, 'auctions/listing.html', {
        'listing': listing,
        'category': listing.get_category_display(),        
        'message': message,
        'bid_form': bid_form,
        'comment_form': comment_form,
        'label': label,
        'number_of_bids': listing.bids.count(),
        'is_owner': is_owner,        
        'is_winner': is_winner,
        'in_watchlist': in_watchlist,
        'comments': listing.comments.all()
    })

@login_required
def Watchlist(request, listing_id):
    listing = Listing.objects.get(pk = listing_id)
    
    if listing in request.user.watchlist.listings.all():
        request.user.watchlist.listings.remove(listing)
        request.user.watchlist.save()
    else:
        request.user.watchlist.listings.add(listing)
        request.user.watchlist.save()
    return HttpResponseRedirect(reverse("listing", args=[listing_id]))

@login_required
def close_listing(request, listing_id):
    listing = Listing.objects.get(pk = listing_id)
    listing.is_active = False
    listing.save()
    return HttpResponseRedirect(reverse("listing", args=[listing_id]))

def MyWatchlist(request):
    return render(request, "auctions/index.html", {
        'listings': request.user.watchlist.listings.all(),
        'title': "Watchlist"
    })

def Categories(request):
    categories = []
    for choice in Listing.CATEGORY_CHOICES:
        categories.append(choice[1])
    return render(request, "auctions/categories.html", {
        'categories': categories
    })

def Category(request, category):
    for choice in Listing.CATEGORY_CHOICES:
        if choice[1] == category:
            key = choice[0]
            break
    listings = Listing.objects.filter(category = key, is_active = True)
    if category == 'No category':
        title = "Active listings without category"
    else:
        title = f"Active listings from category {category}"
    return render(request, "auctions/index.html", {
        'title': title,
        'listings': listings
    })

def user(request, user_id):
    try:
        user = User.objects.get(pk = user_id)
    except User.DoesNotExist:
        raise Http404("User not found.")
    
    wins = []
    listings = []
    for listing in Listing.objects.all():
        if listing.bids.count()>0 and listing.bids.latest('id').bidder.id == user_id and listing.is_active == False:
            wins.append(listing)
        if listing.owner.id == user_id:
            listings.append(listing)
    return render(request, "auctions/user.html",{
        'is_staff': user.is_staff,
        'name': user.username,
        'wins': wins,
        'listings': listings,
        'my_page': request.user.id == user_id
    })