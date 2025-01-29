# urls.py
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Authentication URLs
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('signup/', views.signup, name='signup'),
    path('password-reset/', 
         auth_views.PasswordResetView.as_view(template_name='password_reset.html'),
         name='password_reset'),
    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'),
         name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'),
         name='password_reset_confirm'),
    
    # Main URLs
    path('', views.home, name='home'),
    path('profile/', views.profile, name='profile'),
    
    # Expense URLs
    path('expenses/', views.expense_list, name='expenses'),
    path('expenses/add/', views.add_expense, name='add_expense'),
    # path('expenses/<int:pk>/edit/', views.edit_expense, name='edit_expense'),
    
    # Budget URLs
    path('budgets/', views.budget_list, name='budgets'),
    path('budgets/add/', views.add_budget, name='add_budget'),
    # path('budgets/<int:pk>/edit/', views.edit_budget, name='edit_budget'),
    
    # Goal URLs
    path('goals/', views.goal_list, name='goals'),
    path('goals/add/', views.add_goal, name='add_goal'),
    # path('goals/<int:pk>/edit/', views.edit_goal, name='edit_goal'),
    
    # Report URLs
    path('reports/', views.reports, name='reports'),
    # path('reports/generate/', views.generate_report, name='generate_report'),
    # path('reports/<int:pk>/', views.report_detail, name='report_detail'),
    
    # Settings URLs
    path('settings/', views.settings, name='settings'),
    # path('settings/notifications/', views.notifications, name='notifications'),
]