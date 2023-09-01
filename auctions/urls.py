from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create, name="create"),
    path("listing/<str:id>", views.listing, name="listing"),
    path("close", views.close, name="close"),
    path("comment", views.comment, name="comment"),
    path("bid", views.bid, name="bid"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("category/<str:category_name>", views.category, name="category")
]

urlpatterns = urlpatterns + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)