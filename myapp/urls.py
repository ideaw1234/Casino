from django.urls import path,include
from myapp import views
# from django.contrib.auth import views as auth_views


urlpatterns = [
    path('',views.index,name="home"),
    
    path('register',view=views.register,name="register"),
    path('register_thankyou',view=views.register_thankyou,name="register_thankyou"),
    path('activate/<str:uidb64>/<str:token>',view=views.activate,name="activate"),
    # path('dashboard',view=views.dashboard,name="dashboard"),
    path('transfertoadmin',view=views.transfertoadmin,name="transfertoadmin"),
    path('transfertouser',view=views.transfertouser,name="transfertouser"),
    path('trasaction',view=views.trasaction,name="trasaction"),
    path('profile',view=views.profile,name="profile"),
    # path('login/', auth_views.LoginView.as_view(), name='login'),
    path('',include('django.contrib.auth.urls')),
]

