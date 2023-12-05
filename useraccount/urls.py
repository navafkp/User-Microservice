from django.urls import path
from .views import RegisterView, UserDetails,UserUpdate,GetallUsers,BlockUser,UserAuthentication

# Use to get JWT access and refresh token for user login 
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', RegisterView.as_view(), name='register_user'),
    path('user/details/', UserDetails.as_view(), name='user_detail'),
    path('user/update/', UserUpdate.as_view(), name='user_update'),
    path('user/all-users/', GetallUsers.as_view(), name='get_all_user'),
    path('user/action/<int:id>/', BlockUser.as_view(), name='block_user'),
    path('user-authenticate/', UserAuthentication.as_view(), name='user_authentication'),
    
    
    
]
