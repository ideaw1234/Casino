from django import forms
from django.contrib.auth.forms import UserCreationForm

from myapp.models import Profile,CustomUser


class RegisterForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = UserCreationForm.Meta.fields + ("email",)


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ("first_name", "last_name")

class ExtendedProfileForm(forms.ModelForm):
    prefix="extended"
    class Meta:
        model = Profile
        fields  = ("phone",)

class UserTransferForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ("user",)

class TransferPoint(forms.ModelForm):
    class Meta:
        model = Profile
        fields  = ("point",)
        
class TransferPointAdminForm(forms.Form):
    points = forms.IntegerField()
    admin_users = forms.ModelChoiceField(
        queryset=CustomUser.objects.filter(is_staff=True), 
        required=True, 
        empty_label="เลือกแอดมิน"
    )
    
class TransferPointUserForm(forms.Form):
    points = forms.IntegerField()
    users = forms.ModelChoiceField(
        queryset=CustomUser.objects.filter(is_active=True,is_staff=False), 
        required=True, 
        empty_label="เลือก user"
    )