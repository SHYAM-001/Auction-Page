from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User,Category,Listing,Comment,Bid


def index(request):
    activeListings = Listing.objects.filter(isActive = True)
    allCategories = Category.objects.all()
    return render(request, "auctions/index.html",{
        "listings":activeListings,
        "categories":allCategories
    })

def displayCategory(request):
    if request.method == "POST":
        categoryFromForm = request.POST['category']
        if categoryFromForm == "":
            return HttpResponseRedirect(reverse(index))
        else:
            category = Category.objects.get(categoryName = categoryFromForm)
            activeListings = Listing.objects.filter(isActive = True,category = category)
            allCategories = Category.objects.all()
            return render(request, "auctions/index.html",{
                "listings":activeListings,
                "categories":allCategories
            })

def createListing(request):
    if request.method == "GET":
        allCategories = Category.objects.all()
        return render(request,"auctions/create.html",{
            "categories":allCategories
        })
    else:
        # Get the data from the form
        title = request.POST['title']
        description = request.POST['description']
        imageurl = request.POST['imageurl']
        price = request.POST['price']
        category = request.POST['category']
        
        # Who is the user
        currentUser = request.user
        
        # Get all content about the particular category
        categoryData = Category.objects.get(categoryName=category)
        
        # Create a bid object
        bid = Bid(bids=int(price),user=currentUser)
        bid.save()    

        #Create a new listing object
        newListing = Listing(
            title=title,
            description=description,
            imageUrl = imageurl,
            price =bid,
            category = categoryData,
            owner = currentUser
        )
        
        # Insert the object in our database
        newListing.save()
        
        # Redirect to index page
        return HttpResponseRedirect(reverse(index))
    
def listing(request,id):
    listingData = Listing.objects.get(pk=id)
    isListingInWatchList = request.user in listingData.watchlist.all()
    allComments = Comment.objects.filter(listing = listingData)
    isOwner = request.user.username == listingData.owner.username
    return render(request,"auctions/listing.html",{
        "listing":listingData,
        "isListingInWatchList":isListingInWatchList,
        "allComments": allComments,
        "isOwner":isOwner
    })
  
def classAuction(request,id):
    listingData = Listing.objects.get(pk=id)
    listingData.isActive = False
    listingData.save()
    isListingInWatchList = request.user in listingData.watchlist.all()
    allComments = Comment.objects.filter(listing = listingData)
    isOwner = request.user.username == listingData.owner.username
    return render(request,"auctions/listing.html",{
        "listing":listingData,
        "isListingInWatchList":isListingInWatchList,
        "allComments": allComments,
        "isOwner":isOwner,
        "message":"Congratulations! Your auction is Closed."
    })


  
def removewatchlist(request,id):
    listingData = Listing.objects.get(pk=id)
    currentUser = request.user
    listingData.watchlist.remove(currentUser)
    return HttpResponseRedirect(reverse(listing,args=(id, )))
    
def addwatchlist(request,id):
    listingData = Listing.objects.get(pk=id)
    currentUser = request.user
    listingData.watchlist.add(currentUser)
    return HttpResponseRedirect(reverse(listing,args=(id, )))

def displaywatchlist(request):
    currentUser = request.user
    listings = currentUser.listingwatchlist.all()
    return render(request, "auctions/watchlist.html",{
        "listings":listings
    })

def addComment(request,id):
    currenUser = request.user
    listingData = Listing.objects.get(pk=id)
    message = request.POST['newcomment']
    
    newComment = Comment(
        author = currenUser,
        listing = listingData,
        message = message
    )
    
    newComment.save()
    
    return HttpResponseRedirect(reverse(listing,args=(id, )))

def addbid(request,id):
    newbid = request.POST['addbid']
    listingData = Listing.objects.get(pk=id)
    isListingInWatchList = request.user in listingData.watchlist.all()
    allComments = Comment.objects.filter(listing = listingData)
    isOwner = request.user.username == listingData.owner.username
    if int(newbid) > listingData.price.bids:
        updatebid = Bid(user=request.user,bids=int(newbid))
        updatebid.save()
        listingData.price = updatebid
        listingData.save()
        return render(request,"auctions/listing.html",{
            "listing":listingData,
            "message":" Bid was Updated Successfully",
            "update" : True,
            "isOwner":isOwner,
            "isListingInWatchList":isListingInWatchList,
            "allComments": allComments
        })
    else:
        return render(request,"auctions/listing.html",{
            "listing":listingData,
            "message":" Bid was Update Failed",
            "update" : False,
            "isOwner":isOwner
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
