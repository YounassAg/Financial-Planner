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
    path('expenses/', views.expenses, name='expenses'),
    path('expenses/add/', views.add_expense, name='add_expense'),
    path('expenses/edit/<int:expense_id>/', views.edit_expense, name='edit_expense'),
    path('expenses/delete/<int:expense_id>/', views.delete_expense, name='delete_expense'),
    
    # Budget URLs
    path('budgets/', views.budgets, name='budgets'),
    path('budgets/add/', views.add_budget, name='add_budget'),
    path('budgets/edit/<int:budget_id>/', views.edit_budget, name='edit_budget'),
    path('budgets/delete/<int:budget_id>/', views.delete_budget, name='delete_budget'),
    
    # Income URLs
    path('income/', views.income, name='income'),
    path('income/add/', views.add_income, name='add_income'),
    path('income/edit/<int:income_id>/', views.edit_income, name='edit_income'),
    path('income/delete/<int:income_id>/', views.delete_income, name='delete_income'),
    
    # Budget URLs
    path('budgets/', views.budget_list, name='budgets'),
    path('budgets/add/', views.add_budget, name='add_budget'),
    # path('budgets/<int:pk>/edit/', views.edit_budget, name='edit_budget'),

    # Categories URLs
    path('categories/', views.categories, name='categories'),
    path('categories/add/', views.add_category, name='add_category'),
    path('categories/edit/<int:category_id>/', views.edit_category, name='edit_category'),
    path('categories/delete/<int:category_id>/', views.delete_category, name='delete_category'),
    
    # Goal URLs
    path('goals/', views.goals, name='goals'),
    path('goals/add/', views.add_goal, name='add_goal'),
    path('goals/edit/<int:goal_id>/', views.edit_goal, name='edit_goal'),
    path('goals/delete/<int:goal_id>/', views.delete_goal, name='delete_goal'),
    
    # Report URLs
    path('reports/', views.reports, name='reports'),
    path('reports/generate/', views.generate_report, name='generate_report'),
    path('reports/<int:report_id>/', views.report_detail, name='report_detail'),
    path('reports/<int:report_id>/download/', views.download_report, name='download_report'),
    
    # Settings URLs
    path('settings/', views.settings, name='settings'),
    # path('settings/notifications/', views.notifications, name='notifications'),
]