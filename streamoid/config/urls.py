"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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
from django.urls import include, path

from mapping.api.v1 import urls as mapping_urls
from marketplace.api.v1 import urls as marketplace_urls
from seller.api.v1 import urls as seller_urls

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/marketplace/", include(marketplace_urls)),
    path("api/v1/mapping/", include(mapping_urls)),
    path("api/v1/seller/", include(seller_urls)),
]
