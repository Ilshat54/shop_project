from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('cart/', views.cart_view, name='cart'),
    path('login/', views.login_view, name='login'),
    path('category/<int:category_id>/', views.category_view, name='category'),
    path('product/<int:product_id>/', views.product_view, name='product'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path("register/", views.register_view, name="register"),
    path("logout/", views.logout_view, name="logout"),
    path("profile/", views.profile_view, name="profile"),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:product_id>/', views.update_cart, name='update_cart'),
    path('cart/remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('orders/', views.orders_list, name='orders_list'),
    path("orders/history/", views.orders_history, name="orders_history"),
    path("admin-panel/", views.admin_panel, name="admin_panel"),
    path("admin-panel/delete-user/<int:user_id>/", views.delete_user, name="delete_user"),
    path("admin-panel/delete-product/<int:product_id>/", views.delete_product, name="delete_product"),
    path("admin-panel/change-status/<int:order_id>/", views.change_order_status, name="change_order_status"),
    path("admin-panel/add-product/", views.add_product, name="add_product"),
    path("admin-panel/edit-product/<int:product_id>/", views.edit_product, name="edit_product"),
    path("search/", views.search, name="search"),
    path("search_suggestions/", views.search_suggestions, name="search_suggestions"),


]
