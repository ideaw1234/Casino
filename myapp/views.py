from django.core.mail import EmailMessage
from django.shortcuts import render
from django.http import HttpResponse,HttpRequest,HttpResponseRedirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, permission_required
from django.urls import reverse,reverse_lazy
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.core.exceptions import PermissionDenied
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.utils import timezone

from myapp.models import Profile,CustomUser
from myapp.forms import *
from myapp.utils.activation_token_generator import activation_token_generator
import time

# Create your views here.
def index(request: HttpRequest):

    CustomUsers = get_user_model()
    all_Profile = Profile.objects.filter(user__is_staff=False).order_by("-point")
    context = {"all_Profile":all_Profile}
    return render(request,"index.html",context) 

def about(request):
    return render(request,"about.html")
def register(request: HttpRequest):
    #POST
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            #Register
            user:CustomUser = form.save(commit=False)
            user.is_active = False
            user.save()
            profile = Profile(user=user, phone='0000000000')
            profile.point = 50
            profile.date = timezone.now()
            profile.save()
            group = Group.objects.get(name='Players')
            user.groups.add(group)
            #login(request,user)
            #Build emaill HTML
            context = {
                "protocol":request.scheme,
                "host":request.get_host(),
                "uidb64": urlsafe_base64_encode(force_bytes(user.id)),
                "token":activation_token_generator.make_token(user),
            }
            email_body = render_to_string("activate_email.html",context=context)
            #send maill
            email = EmailMessage(
                to=[user.email],
                subject="Active account",
                body = email_body
            )
            email.send()
            
            return HttpResponseRedirect(reverse("register_thankyou"))
    else:
        form = RegisterForm()
    #FET
    context = {"form":form}
    return render(request,"register.html",context)

def register_thankyou(request: HttpRequest):
    return render(request,"register_thankyou.html")

def activate(request: HttpRequest,uidb64:str,token: str):
    title = "Activate account เรียบร้อย"
    description = "คุณสามารถเข้าสู่ระบบได้เลย"
    id = urlsafe_base64_decode(uidb64).decode()
    try:
        user: CustomUser = CustomUser.objects.get(id=id)
        if not activation_token_generator.check_token(user,token):
            raise Exception("Check token false")
        user.is_active = True
        user.save()
    except:
        title = "Activate account ไม่ได้"
        description = "ลิงค์อาจถูกใช้ไปแล้ว หรือหมดอายุ"
    
    context = {"title":title,"description":description}
    return render(request,"activate.html",context)

# @login_required
# def dashboard(request: HttpRequest):
#     return render(request,"dashboard.html")

@login_required
def transfertoadmin(request:HttpRequest):
    point_user = Profile.objects.get(user = request.user)
    flash_message = ""
    if request.method == 'POST':
        form = TransferPointAdminForm(request.POST)
        if form.is_valid():
            points = form.cleaned_data['points']
            recipient = form.cleaned_data['admin_users']
            
            sender_points = Profile.objects.get(user=request.user)
            recipient_points = Profile.objects.get(user=recipient)
            print(recipient_points)
            print(sender_points)
            if sender_points.point < points:
                flash_message = "แต้มไม่พอลองอีกครั้ง"
                form = TransferPointAdminForm()
            else:
                sender_points.point -= points
                recipient_points.point += points
                sender_points.save()
                recipient_points.save()
                flash_message = "ส่งแต้มสำเร็จ"
                point_user = Profile.objects.get(user_id = request.user)
                form = TransferPointAdminForm()
                
    else:
        form = TransferPointAdminForm()
    context= {
        "flash_message": flash_message,
        'form': form,
        "point_user":point_user
    }
    return render(request, 'transferToadmin.html',context)

@login_required
def transfertouser(request:HttpRequest):
    if not request.user.is_staff:
        raise PermissionDenied()
    point_user = Profile.objects.get(user_id =request.user)
    flash_message = ""
    if request.method == 'POST':
        # Handle POST request
        form = TransferPointUserForm(request.POST)
        if form.is_valid():
            points = form.cleaned_data['points']
            recipient = form.cleaned_data['users']
            
            sender_points = Profile.objects.get(user=request.user)
            recipient_points = Profile.objects.get(user=recipient)
            print(recipient_points)
            print(sender_points)
            if sender_points.point < points:
                flash_message = "แต้มไม่พอลองอีกครั้ง"
                form = TransferPointUserForm()
            else:
                sender_points.point -= points
                recipient_points.point += points
                sender_points.save()
                recipient_points.save()
                flash_message = "ส่งแต้มสำเร็จ"
                point_user = Profile.objects.get(user_id = request.user)
                form = TransferPointUserForm()
    else:
        # Handle GET request
        form = TransferPointUserForm()
    context= {
        "flash_message": flash_message,
        'form': form,
        "point_user":point_user
    }
    return render(request, 'transferTouser.html',context)



@login_required
def profile(request: HttpRequest):
    user = request.user

    # POST
    if request.method == "POST":
        form = UserProfileForm(request.POST, instance=user)
        is_new_profile = False
        try:
            # Will be updated profile
            extended_form = ExtendedProfileForm(request.POST, instance=user.profile)
        except:
            # Will be created profile
            extended_form = ExtendedProfileForm(request.POST)
            is_new_profile = True
            

        if form.is_valid() and extended_form.is_valid():
            form.save()
            if is_new_profile:
                # Create profile
                profile = extended_form.save(commit=False)
                profile.user = user
                profile.save()
            else:
                # Update profile
                extended_form.save()
            response = HttpResponseRedirect(reverse("profile"))
            response.set_cookie("is_saved", "1")
            return response
    else:
        form = UserProfileForm(instance=user)
        try:
            extended_form = ExtendedProfileForm(instance=user.profile)
        except:
            extended_form = ExtendedProfileForm()

    # GET
    is_saved = request.COOKIES.get("is_saved") == "1"
    flash_message = "บันทึกเรียบร้อย" if is_saved else None
    context = {
        "form": form,
        "extended_form": extended_form,
        "flash_message": flash_message,
    }
    response = render(request, "profile.html", context)
    if is_saved:
        response.delete_cookie("is_saved")
    return response