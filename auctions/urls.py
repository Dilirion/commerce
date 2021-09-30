from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create, name="create"),
    path("listing/<int:listing_id>", views.listing, name="listing"),
    path("listing/watchlist/<int:listing_id>", views.Watchlist, name="watchlist"),
    path("close/<int:listing_id>", views.close_listing, name="close_listing"),
    path("mywatchlist", views.MyWatchlist, name="mywatchlist"),
    path("categories", views.Categories, name = "categories"),
    path("catgories/<str:category>", views.Category, name="category"),
    path("user/<int:user_id>", views.user, name="user")
]
