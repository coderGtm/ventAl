from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import *


# Create your forms here.

# form for creating a new user
class NewUserForm(UserCreationForm):
	email = forms.EmailField(required=True)

	class Meta:
		model = User
		fields = ("username", "email", "password1", "password2")

	def save(self, commit=True):
		user = super(NewUserForm, self).save(commit=False)
		user.email = self.cleaned_data['email']
		if commit:
			user.save()
		return user

# form for uploading multiple images
class ImageUploadForm(forms.Form):
	images = forms.ImageField(widget=forms.ClearableFileInput(attrs={'multiple': True, 'required': True}))

# form for album name with default value
class AlbumNameForm(forms.Form):
	album_name = forms.CharField(label="Album Name:", max_length=100, required=True)

# form for cover image
class CoverImageForm(forms.Form):
	cover_image = forms.ImageField(widget=forms.ClearableFileInput(attrs={'required': True}))

# form for album pin
class AlbumPinForm(forms.Form):
	album_pin = forms.CharField(label="Album Pin:", max_length=4, required=True)