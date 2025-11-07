from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views

from contacts.views import add_contact, frontpage, signup, share_contact, unshare_contact
from contacts import views as contact_views
    
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', frontpage, name='frontpage'),
    path('add/', add_contact, name='add_contact'),
    path('contacts/<int:pk>/edit/', contact_views.edit_contact, name='edit_contact'),
    path('contacts/<int:pk>/delete/', contact_views.delete_contact, name='delete_contact'),
    path('contacts/<int:pk>/share/', share_contact, name='share_contact'),
    path('contacts/<int:pk>/unshare/<int:user_id>/', unshare_contact, name='unshare_contact'),
    path('signup/', signup, name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]
