from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from myapp.models import Profile,CustomUser,Transaction
# Register your models here.
admin.site.register(Profile),
admin.site.register(Transaction),
admin.site.register(CustomUser,UserAdmin)