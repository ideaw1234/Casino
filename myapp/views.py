from django.core.mail import EmailMessage
from django.shortcuts import render,redirect
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
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.core.paginator import Paginator

from myapp.models import Profile,CustomUser,Transaction
from myapp.forms import *
from myapp.utils.activation_token_generator import activation_token_generator
import time

# Create your views here.
def index(request: HttpRequest):

    CustomUsers = get_user_model()
    all_Profile = Profile.objects.filter(user__is_staff=False).order_by("-point")
    paginator = Paginator(all_Profile, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    context = {
        "all_Profile":page.object_list,
        "page": page
        }
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
            profile = Profile(user=user, phone='')
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
# def login_view(request):
#     if request.method == 'POST':
#         form = AuthenticationForm(request, data=request.POST)
#         if form.is_valid():
#             user = form.get_user()
#             if user.is_active:
#                 login(request, user)
#                 return redirect('home')
#             else:
#                 # Return an 'inactive account' error message.
#                 form.add_error(None, 'Your account is inactive.')
#     else:
#         form = AuthenticationForm()
#     return render(request, 'login.html', {'form': form})

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
                transaction = Transaction(sender=request.user, recipient=recipient, points=points)
                transaction.save()
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
                transaction = Transaction(sender=request.user, recipient=recipient, points=points)
                transaction.save()
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
def trasaction(request:HttpRequest):
    all_transactions = Transaction.objects.all().order_by('-timestamp')
    user_transactions = Transaction.objects.filter(sender=request.user).order_by('-timestamp')
    recipient_transactions = Transaction.objects.filter(recipient=request.user).order_by('-timestamp')
    per_page = 10
    all_paginator = Paginator(all_transactions, per_page)
    all_page_number = request.GET.get('page')
    all_page_obj = all_paginator.get_page(all_page_number)
    user_paginator = Paginator(user_transactions, per_page)
    user_page_number = request.GET.get('page')
    user_page_obj = user_paginator.get_page(user_page_number)
    recipient_paginator = Paginator(recipient_transactions, per_page)
    recipient_page_number = request.GET.get('page')
    recipient_page_obj = recipient_paginator.get_page(recipient_page_number)
    combined_transactions = user_transactions | recipient_transactions
    combined_paginator = Paginator(combined_transactions, per_page)
    combined_page_number = request.GET.get('page')
    combined_page_obj = combined_paginator.get_page(combined_page_number)
    


    context = {
        "all_page_obj": all_page_obj,
        "all_paginator": all_paginator,
        "user_transactions": user_transactions,
        "user_paginator":user_paginator,
        "user_page_obj":user_page_obj,
        "recipient_transactions":recipient_transactions,
        "recipient_page_obj": recipient_page_obj,
        "recipient_paginator": recipient_paginator,
        "combined_page_obj": combined_page_obj,
        "combined_paginator": combined_paginator,
    }
    return render(request, 'trasaction.html',context)
    


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