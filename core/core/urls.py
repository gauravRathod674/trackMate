"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from home.views import *
from trackmate.views import *
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns


urlpatterns = [
    path("admin/", admin.site.urls),
    path("homepage/", homepage, name="homepage"),
    path("mobile/", mobile, name="mobile"),
    path("laptop/", laptop, name="laptop"),
    path("audio/", audio, name="audio"),
    path("books/", books, name="books"),
    path("footwear/", footwear, name="footwear"),
    path("petFood/", petFood, name="petFood"),
    path("watches/", watches, name="watches"),
    path("clothes/", clothes, name="clothes"),
    path("camera/", camera, name="camera"),
    path("contact/", contact, name="contact"),
    path("about/", aboutUs, name="aboutUs"),
    path("login/", loginPage, name="loginPage"),
    path("register/", registerPage, name="registerPage"),
    path("search/", search, name="search"),
    path("Search/<str:productName>/", Search, name="Search"),
    path("", homepage, name="homepage"),
    path("logout/", logoutView, name="logoutView"),
    path("userProfile/", userProfileSetting, name="userProfileSetting"),
    path("deactivate_account/", deactivate_account, name="deactivate_account"),
    path("celery/", include("trackmate.urls")),
    path("alertlist/", alertlist, name="alertlist"),
    path("wishlist/", wishlist, name="wishlist"),
    path("recentSearch/", recentSearch, name="recentSearch"),
    path("clearHistory/", clearHistory, name="clearHistory"),
    path(
        "deleteRecentSearchProduct/<id>/",
        deleteRecentSearchProduct,
        name="deleteRecentSearchProduct",
    ),
    path(
        "removeItemFromWishlist/", removeItemFromWishlist, name="removeItemFromWishlist"
    ),
    path("removeItemFromAlert/", removeItemFromAlert, name="removeItemFromAlert"),
    path("banner/", banner, name="banner"),
    path("check_authentication/", check_authentication, name="check_authentication"),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


urlpatterns += staticfiles_urlpatterns()
