from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from .models import UserProfile

class RegistrationForm(UserCreationForm): # modelform use korini karon: ekhane jeshob field dekhate hobe shegulo usercreation form er moddhei ache
    class Meta: # akta class er moddhe extra characteristics add korte help kore
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']    

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['bio', 'profile_image']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['profile_image'].widget.attrs.update({'class': 'custom-file-input'})  # Add any custom styling classes here
