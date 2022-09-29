"""iert URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
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

from django.urls import path, include
from django.conf import settings
from . import views
from django.conf.urls.static import static

urlpatterns = [
        path('index/', views.index, name='index'),
        path('', views.home),
        path('cart/', views.cart),
        path('shop/', views.shop),
        path('checkout/',views.checkout),
        path('details/',views.details),
        path('contact/',views.contact),
        path('about/',views.about),
        path('shop/ToCart/', views.ToCart, name='ToCart'),
        path('cart/ToCart/', views.ToCart, name='ToCart'),
        path('shopdetails/ToCart/', views.ToCart, name='ToCart'),
        path('cart/FromCart/', views.FromCart, name='FromCart'),
        path('cart/remove/', views.remove, name='remove'),
        path('shop/<str:id>', views.shopview, name="shopview"),
        path('shopdetails/<int:id>', views.shopdetails, name='shopdetails'),
        path('home2/',views.HomePageView.as_view(), name='home'),
        path('checkout/sales/',views.sales),
        path('charge/',views.charge, name='charge'),
]
