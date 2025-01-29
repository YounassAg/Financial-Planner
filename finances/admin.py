from django.contrib import admin
from .models import Profile, Category, Expense, Budget, Goal, Transaction, Report

admin.site.register(Profile)
admin.site.register(Category)
admin.site.register(Expense)
admin.site.register(Budget)
admin.site.register(Goal)
admin.site.register(Transaction)
admin.site.register(Report)