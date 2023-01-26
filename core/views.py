import string
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import NewUserForm, ImageUploadForm, AlbumNameForm, CoverImageForm, AlbumPinForm
from django.contrib.auth import login
from django.contrib import messages
from .__init__ import ref, cloud_bucket
from firebase_admin import db as rtdb
import random


# Create your views here.


@login_required
def showDashboard(request):
    username = request.user.username
    try:
        storage_used = str(round(float(ref.child(username).child("storage").get()),2))
    except:
        storage_used = "0"
    albums = ref.child(username).child("albums").get()
    if albums is None:
        albums = {}
    album_ids = list(albums.keys())
    albumNames = list(albums.values())
    album_cover_urls = []
    for i in range(len(albumNames)):
        albumNames[i] = albumNames[i]['name']
        album_cover_urls.append(albums[album_ids[i]]['cover'])
    albumArray = []
    for i in range(len(album_ids)):
        albumArray.append([album_ids[i],albumNames[i],album_cover_urls[i]])
    return render(request, 'core/dashboard.html', context={"username":username,"storage_used":storage_used,"album_array":albumArray,"navTitle":"Dashboard"})




@login_required
def stage(request, album_id):

    username = request.user.username
    album_name = ref.child(username).child("albums").child(album_id).child("name").get()
    if album_name is None and album_id != "new":
        return render(request, 'core/invalid-stage.html', context={"username":username})
    if album_id == "new":
        #generate unique id
        album_id = ref.child(username).child("albums").push().key
        album_name = "Untitled"
        # generate a random 4 digit pin
        album_pin = str(random.randint(1000,9999))
        #set a random cover image
        cover_img_url = "https://firebasestorage.googleapis.com/v0/b/" + cloud_bucket.name + "/o/sample-cover-images%2Fcover-" + str(random.randint(1,6)) + ".webp?alt=media"
        ref.child(username).child("albums").child(album_id).set({"name":album_name,"pin":album_pin,"cover":cover_img_url})
        album_ref_id = generateRefId()
        rtdb.reference("mapping").child(album_ref_id).set({"username":username,"album_id":album_id})
        #ref.child("mapping").child(album_ref_id).set({"username":username,"album_id":album_id})
        ref.child(username).child("albums").child(album_id).child("ref_id").set(album_ref_id)
        return redirect("stage", album_id=album_id)
    else:
        album_pin = ref.child(username).child("albums").child(album_id).child("pin").get()
        cover_img_url = ref.child(username).child("albums").child(album_id).child("cover").get()
        album_ref_id = ref.child(username).child("albums").child(album_id).child("ref_id").get()


    imageURLs = ref.child(username).child("albums").child(album_id).child("images").get()
    if imageURLs is None:
        imageURLs = []
    else:
        for key in imageURLs.keys():
            imageURLs[key] = {
                "view": "https://firebasestorage.googleapis.com/v0/b/" + cloud_bucket.name + "/o/" + album_id + "%2F" + key + "." + imageURLs[key] + "?alt=media",
                "delete": "/delete/image/{}/{}/{}".format(username,album_id,key),
                "size": round(cloud_bucket.get_blob(album_id + "/" + key + "." + imageURLs[key]).size / 1000, 2)
            }
        imageURLs = imageURLs.values()

    if request.method == "POST":
        if "imgUploadBtn" in request.POST:
            imgForm = ImageUploadForm(request.POST, request.FILES)
            if imgForm.is_valid():
                uploadedImages = request.FILES.getlist('images')
                print(uploadedImages)
                for image in uploadedImages:
                    #generate short unique image name
                    imgKey = ref.child(username).child("albums").child(album_id).child("images").push().key
                    imgExtension = image.name.split(".")[-1]
                    image.name = imgKey + "." + imgExtension
                    #upload to cloud
                    blob = cloud_bucket.blob(album_id + "/" + image.name)
                    blob.upload_from_file(image, content_type=image.content_type)
                    #update database
                    ref.child(username).child("albums").child(album_id).child("images").child(imgKey).set(imgExtension)
                    #update storage
                    storage_used = ref.child(username).child("storage").get()
                    imgSizeInMB = image.size / 1000000
                    ref.child(username).child("storage").set(storage_used + imgSizeInMB)
                return redirect("stage", album_id=album_id)
        
        elif "nameChangeBtn" in request.POST:
            album_name_form = AlbumNameForm(request.POST)
            if album_name_form.is_valid():
                album_name = album_name_form.cleaned_data['album_name']
                ref.child(username).child("albums").child(album_id).child("name").set(album_name)
                return redirect("stage", album_id=album_id)

        elif "coverImgUploadBtn" in request.POST:
            coverImgForm = CoverImageForm(request.POST, request.FILES)
            if coverImgForm.is_valid():
                image = request.FILES['cover_image']
                image.name = "cover." + image.name.split(".")[-1]
                #upload to cloud
                blob = cloud_bucket.blob(album_id + "/" + image.name)
                blob.upload_from_file(image, content_type=image.content_type)
                #update database
                ref.child(username).child("albums").child(album_id).child("cover").set("https://firebasestorage.googleapis.com/v0/b/" + cloud_bucket.name + "/o/" + album_id + "%2F" + image.name + "?alt=media")
                return redirect("stage", album_id=album_id)
                

    albumNameForm = AlbumNameForm(initial={"album_name":album_name})
    imgForm = ImageUploadForm()
    coverImgForm = CoverImageForm()
    
    return render(request, 'core/stage.html', context={"username":username,"album_id":album_id,"album_name":album_name,"album_pin":album_pin,"name_form":albumNameForm,"img_form":imgForm,"coverImg_form": coverImgForm,"image_urls":imageURLs,"cover_img_url":cover_img_url,"album_ref_id":album_ref_id, "navTitle":"Stage"})


def album(request, album_ref):
    album_ref_id = album_ref
    album_id = rtdb.reference("mapping").child(album_ref_id).child("album_id").get()
    username = rtdb.reference("mapping").child(album_ref_id).child("username").get()
    if album_id is None or username is None:
        return render(request, 'core/invalid-album.html')
    album_name = ref.child(username).child("albums").child(album_id).child("name").get()
    album_pin = ref.child(username).child("albums").child(album_id).child("pin").get()
    cover_img_url = ref.child(username).child("albums").child(album_id).child("cover").get()

    if request.method == "POST":
        pinForm = AlbumPinForm(request.POST)
        if pinForm.is_valid():
            pin = pinForm.cleaned_data['album_pin']
            if pin == album_pin:
                imageURLs = ref.child(username).child("albums").child(album_id).child("images").get()
                if imageURLs is None:
                    imageURLs = []
                else:
                    for key in imageURLs.keys():
                        imageURLs[key] = {
                            "view": "https://firebasestorage.googleapis.com/v0/b/" + cloud_bucket.name + "/o/" + album_id + "%2F" + key + "." + imageURLs[key] + "?alt=media",
                        }
                    imageURLs = imageURLs.values()
                return render(request, 'core/album.html', context={"album_name":album_name,"cover_img_url":cover_img_url,"image_urls":imageURLs, "authorized":True})
            else:
                messages.error(request, "Incorrect pin")
                return render(request, 'core/album.html', context={"album_name":album_name,"cover_img_url":cover_img_url,"pin_form":pinForm,"authorized":False})
    else:
        pinForm = AlbumPinForm()
        return render(request, 'core/album.html', context={"album_name":album_name,"cover_img_url":cover_img_url,"pin_form":pinForm,"authorized":False})
    
    
    
@login_required
def deleteImage(request, username, album_id, image_id):
    if request.user.username != username or ref.child(username).child("albums").child(album_id).child("images").child(image_id).get() is None:
        return render(request, 'core/invalid-stage.html', context={"username":username})
    #delete from cloud
    imgExtension = ref.child(username).child("albums").child(album_id).child("images").child(image_id).get()
    imgPath = album_id + "/" + image_id + "." + imgExtension
    blob = cloud_bucket.get_blob(imgPath)
    imgSizeInMB = blob.size / 1000000
    blob.delete()
    #delete from database
    ref.child(username).child("albums").child(album_id).child("images").child(image_id).delete()
    #update storage
    storage_used = ref.child(username).child("storage").get()
    ref.child(username).child("storage").set(storage_used - imgSizeInMB)
    return redirect("stage", album_id=album_id)

@login_required
def deleteAlbum(request, username, album_id):
    if request.user.username != username or ref.child(username).child("albums").child(album_id).get() is None:
        return render(request, 'core/invalid-stage.html', context={"username":username})
    #delete from cloud
    albumPath = album_id + "/"
    album_size = 0
    blobs = cloud_bucket.list_blobs(prefix=albumPath)
    for blob in blobs:
        album_size += blob.size
        blob.delete()
    album_size /= 1000000
    #delete from database
    album_ref_id = ref.child(username).child("albums").child(album_id).child("ref_id").get()
    ref.child(username).child("albums").child(album_id).delete()
    #update mapping
    rtdb.reference("mapping").child(album_ref_id).delete()
    #update storage
    storage_used = ref.child(username).child("storage").get()
    if storage_used is None:
        storage_used = 0
    if storage_used - album_size < 0 or storage_used - album_size < 0.0001:
        storage_used = 0
    ref.child(username).child("storage").set(storage_used - album_size)
    return redirect("dashboard")


def signup(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    if request.method == "POST":
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            ref.child(user.username).set({
                'email': user.email,
                "storage": 0,
            })
            login(request, user)
            messages.success(request, "Registration successful." )
            return redirect("dashboard")
        messages.error(request, "Unsuccessful registration. Invalid information.")
    else:
        form = NewUserForm()
    return render(request=request, template_name="registration/signup.html", context={"signup_form":form})

def generateRefId():
    '''generates a random 4 digit string to be used as a reference id'''
    while True:
        ref_id = ''.join(random.choices(string.digits, k=4))
        if rtdb.reference("mapping").child(ref_id).get() is None:
            return ref_id