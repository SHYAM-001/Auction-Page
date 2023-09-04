from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create",views.createListing,name="create"),
    path("displayCategory",views.displayCategory,name="displayCategory"),
    path("listing/<int:id>",views.listing,name="listing"),
    path("removewatchlist/<int:id>",views.removewatchlist,name="removewatchlist"),
    path("addwatchlist/<int:id>",views.addwatchlist,name="addwatchlist"),
    path("watchlist",views.displaywatchlist,name="watchlist"),
    path("addcomment/<int:id>",views.addComment,name="addcomment"),
    path("addbid/<int:id>",views.addbid,name="addbid"),
    path("classauction/<int:id>",views.classAuction,name="classauction"),
]
