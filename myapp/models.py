from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.
# class Profile(models.Model):
#     name = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
#     phone = models.CharField(max_length=15, default="")
#     point = models.IntegerField(default=50)
#     date = models.DateField(auto_now_add=True)

#     def __str__(self):
#         return self.name + " " + "point = " + str(self.point)
class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)

class Profile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    phone = models.CharField(max_length=10, default="0000000000")
    point = models.IntegerField(default=50)
    date = models.DateField(auto_now_add=True)
    
    def __str__(self):
        return self.user.username + " " + str(self.point)