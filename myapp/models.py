from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


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
    phone = models.CharField(max_length=10, default="")
    point = models.IntegerField(default=50)
    date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.user.username + " " + str(self.point)
    
class Transaction(models.Model):
    sender = models.ForeignKey(CustomUser, related_name='sender', on_delete=models.CASCADE)
    recipient = models.ForeignKey(CustomUser, related_name='recipient', on_delete=models.CASCADE)
    points = models.PositiveIntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.sender.username + " ส่งให้ "  + str(self.recipient) + " " + str(self.points) + "แต้ม "+ "เวลา " + str(self.timestamp)