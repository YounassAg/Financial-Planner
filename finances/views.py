from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from .models import Transaction, Category, Budget, Goal, Expense, Report
from .forms import CustomUserCreationForm
from datetime import datetime, timedelta
from django.db.models import Sum
from django.utils import timezone
from django.contrib import messages
from django.http import JsonResponse
import json


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
        
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if username and password:
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                # Get the next parameter from the URL if it exists
                next_url = request.GET.get('next')
                if next_url:
                    return redirect(next_url)
                return redirect('home')
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Please fill in all fields.')
    
    return render(request, 'auth/login.html')

def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)  # Use the custom form
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('home')
    else:
        form = CustomUserCreationForm()  # Use the custom form
    return render(request, 'auth/signup.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('home')

@login_required
def home(request):
    # Get current month's start and end dates
    today = timezone.now()
    month_start = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(seconds=1)

    # Calculate summary metrics
    total_income = Transaction.objects.filter(
        user=request.user,
        transaction_type='INCOME',
        date__range=[month_start, month_end]
    ).aggregate(Sum('amount'))['amount__sum'] or 0

    total_expenses = Transaction.objects.filter(
        user=request.user,
        transaction_type='EXPENSE',
        date__range=[month_start, month_end]
    ).aggregate(Sum('amount'))['amount__sum'] or 0

    net_savings = total_income - total_expenses

    # Calculate budget status
    total_budget = Budget.objects.filter(
        user=request.user,
        start_date__lte=today,
        end_date__gte=today
    ).aggregate(Sum('amount'))['amount__sum'] or 0

    budget_status = (total_expenses / total_budget * 100) if total_budget > 0 else 0

    # Get spending by category
    category_expenses = Transaction.objects.filter(
        user=request.user,
        transaction_type='EXPENSE',
        date__range=[month_start, month_end]
    ).values('category__name').annotate(total=Sum('amount'))

    category_labels = [item['category__name'] for item in category_expenses]
    category_data = [float(item['total']) for item in category_expenses]

    # Get monthly trends (last 6 months)
    months = []
    income_trend = []
    expense_trend = []
    for i in range(5, -1, -1):
        month_date = today - timedelta(days=30*i)
        month_start = month_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(seconds=1)
        
        month_income = Transaction.objects.filter(
            user=request.user,
            transaction_type='INCOME',
            date__range=[month_start, month_end]
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        month_expenses = Transaction.objects.filter(
            user=request.user,
            transaction_type='EXPENSE',
            date__range=[month_start, month_end]
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        months.append(month_date.strftime('%b %Y'))
        income_trend.append(float(month_income))
        expense_trend.append(float(month_expenses))

    # Get recent transactions
    recent_transactions = Transaction.objects.filter(
        user=request.user
    ).order_by('-date')[:5]

    context = {
        'total_income': total_income,
        'total_expenses': total_expenses,
        'net_savings': net_savings,
        'budget_status': round(budget_status, 1),
        'category_labels': json.dumps(category_labels),
        'category_data': json.dumps(category_data),
        'trend_labels': json.dumps(months),
        'income_trend': json.dumps(income_trend),
        'expense_trend': json.dumps(expense_trend),
        'recent_transactions': recent_transactions,
    }

    return render(request, 'dashboard/home.html', context)

@login_required
def expenses(request):
    # Fetch all expenses for the logged-in user
    user_expenses = Expense.objects.filter(user=request.user)
    user_categories = Category.objects.filter(user=request.user)

    # Calculate total spending by category
    spending_by_category = (
        user_expenses.values('category__name')  # Group by category name
        .annotate(total_amount=Sum('amount'))  # Sum the amount for each category
        .order_by('-total_amount')  # Sort by total amount in descending order
    )

    # Prepare data for the chart
    expense_categories = [item['category__name'] for item in spending_by_category]
    expense_amounts = [float(item['total_amount']) for item in spending_by_category]

    return render(request, 'expenses/expenses.html', {
        'expenses': user_expenses,
        'user_categories': user_categories,
        'expense_categories': expense_categories,
        'expense_amounts': expense_amounts,
    })

@login_required
def add_expense(request):
    if request.method == 'POST':
        # Get form data
        amount = request.POST.get('amount')
        category_id = request.POST.get('category')
        date = request.POST.get('date')
        description = request.POST.get('description')
        is_recurring = request.POST.get('is_recurring') == 'on'
        recurrence_frequency = request.POST.get('recurrence_frequency')
        payment_method = request.POST.get('payment_method')

        # Validate and save the expense
        if amount and category_id and date:
            category = Category.objects.get(id=category_id)
            expense = Expense.objects.create(
                user=request.user,
                amount=amount,
                category=category,
                date=date,
                description=description,
                is_recurring=is_recurring,
                recurrence_frequency=recurrence_frequency,
                payment_method=payment_method
            )

            # Create a corresponding transaction for the expense
            Transaction.objects.create(
                user=request.user,
                transaction_type='EXPENSE',
                amount=amount,
                category=category,
                date=date,
                description=description,
                is_recurring=is_recurring,
                recurrence_frequency=recurrence_frequency,
                payment_method=payment_method
            )

            messages.success(request, 'Expense added successfully!')
            return redirect('expenses')
        else:
            messages.error(request, 'Please fill out all required fields.')
    else:
        # Fetch all categories for the dropdown
        categories = Category.objects.filter(user=request.user) | Category.objects.filter(is_default=True)
    return render(request, 'expenses/add_expense.html', {'categories': categories})

@login_required
def edit_expense(request, expense_id):
    expense = get_object_or_404(Expense, id=expense_id, user=request.user)
    if request.method == 'POST':
        # Get form data
        amount = request.POST.get('amount')
        category_id = request.POST.get('category')
        date = request.POST.get('date')
        description = request.POST.get('description')
        is_recurring = request.POST.get('is_recurring') == 'on'
        recurrence_frequency = request.POST.get('recurrence_frequency')
        payment_method = request.POST.get('payment_method')

        # Validate and update the expense
        if amount and category_id and date:
            category = Category.objects.get(id=category_id)
            expense.amount = amount
            expense.category = category
            expense.date = date
            expense.description = description
            expense.is_recurring = is_recurring
            expense.recurrence_frequency = recurrence_frequency
            expense.payment_method = payment_method
            expense.save()

            # Update the corresponding transaction
            transaction = Transaction.objects.filter(
                user=request.user,
                transaction_type='EXPENSE',
                date=expense.date,
                amount=expense.amount,
                category=expense.category
            ).first()

            if transaction:
                transaction.amount = amount
                transaction.category = category
                transaction.date = date
                transaction.description = description
                transaction.is_recurring = is_recurring
                transaction.recurrence_frequency = recurrence_frequency
                transaction.payment_method = payment_method
                transaction.save()
            else:
                # If no corresponding transaction exists, create one
                Transaction.objects.create(
                    user=request.user,
                    transaction_type='EXPENSE',
                    amount=amount,
                    category=category,
                    date=date,
                    description=description,
                    is_recurring=is_recurring,
                    recurrence_frequency=recurrence_frequency,
                    payment_method=payment_method
                )

            messages.success(request, 'Expense updated successfully!')
            return redirect('expenses')
        else:
            messages.error(request, 'Please fill out all required fields.')
    else:
        # Fetch all categories for the dropdown
        categories = Category.objects.filter(user=request.user) | Category.objects.filter(is_default=True)
    return render(request, 'expenses/edit_expense.html', {'expense': expense, 'categories': categories})

@login_required
def delete_expense(request, expense_id):
    expense = get_object_or_404(Expense, id=expense_id, user=request.user)

    # Delete the corresponding transaction
    transaction = Transaction.objects.filter(
        user=request.user,
        transaction_type='EXPENSE',
        date=expense.date,
        amount=expense.amount,
        category=expense.category
    ).first()

    if transaction:
        transaction.delete()

    # Delete the expense
    expense.delete()
    messages.success(request, 'Expense deleted successfully!')
    return redirect('expenses')

@login_required
def budgets(request):
    # Fetch all budgets for the logged-in user
    user_budgets = Budget.objects.filter(user=request.user)
    return render(request, 'budget/budgets.html', {'budgets': user_budgets})

@login_required
def add_budget(request):
    if request.method == 'POST':
        # Get form data
        category_id = request.POST.get('category')
        amount = request.POST.get('amount')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        alert_threshold = request.POST.get('alert_threshold')

        # Validate and save the budget
        if category_id and amount and start_date and end_date:
            category = Category.objects.get(id=category_id)
            Budget.objects.create(
                user=request.user,
                category=category,
                amount=amount,
                start_date=start_date,
                end_date=end_date,
                alert_threshold=alert_threshold
            )
            messages.success(request, 'Budget added successfully!')
            return redirect('budgets')
        else:
            messages.error(request, 'Please fill out all required fields.')
    else:
        # Fetch all categories for the dropdown
        categories = Category.objects.filter(user=request.user) | Category.objects.filter(is_default=True)
    return render(request, 'budget/add_budget.html', {'categories': categories})

@login_required
def edit_budget(request, budget_id):
    budget = get_object_or_404(Budget, id=budget_id, user=request.user)
    if request.method == 'POST':
        # Get form data
        category_id = request.POST.get('category')
        amount = request.POST.get('amount')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        alert_threshold = request.POST.get('alert_threshold')

        # Validate and update the budget
        if category_id and amount and start_date and end_date:
            category = Category.objects.get(id=category_id)
            budget.category = category
            budget.amount = amount
            budget.start_date = start_date
            budget.end_date = end_date
            budget.alert_threshold = alert_threshold
            budget.save()
            messages.success(request, 'Budget updated successfully!')
            return redirect('budgets')
        else:
            messages.error(request, 'Please fill out all required fields.')
    else:
        # Fetch all categories for the dropdown
        categories = Category.objects.filter(user=request.user) | Category.objects.filter(is_default=True)
    return render(request, 'budget/edit_budget.html', {'budget': budget, 'categories': categories})

@login_required
def delete_budget(request, budget_id):
    budget = get_object_or_404(Budget, id=budget_id, user=request.user)
    budget.delete()
    messages.success(request, 'Budget deleted successfully!')
    return redirect('budgets')

@login_required
def income(request):
    # Fetch all income transactions for the logged-in user
    user_income = Transaction.objects.filter(user=request.user, transaction_type='INCOME')
    return render(request, 'income/income.html', {'income': user_income})

@login_required
def add_income(request):
    if request.method == 'POST':
        # Get form data
        amount = request.POST.get('amount')
        category_id = request.POST.get('category')
        date = request.POST.get('date')
        description = request.POST.get('description')
        is_recurring = request.POST.get('is_recurring') == 'on'
        recurrence_frequency = request.POST.get('recurrence_frequency')
        payment_method = request.POST.get('payment_method')

        # Validate and save the income
        if amount and category_id and date:
            category = Category.objects.get(id=category_id)
            Transaction.objects.create(
                user=request.user,
                transaction_type='INCOME',
                amount=amount,
                category=category,
                date=date,
                description=description,
                is_recurring=is_recurring,
                recurrence_frequency=recurrence_frequency,
                payment_method=payment_method
            )
            messages.success(request, 'Income added successfully!')
            return redirect('income')
        else:
            messages.error(request, 'Please fill out all required fields.')
    else:
        # Fetch all categories for the dropdown
        categories = Category.objects.filter(user=request.user) | Category.objects.filter(is_default=True)
    return render(request, 'income/add_income.html', {'categories': categories})

@login_required
def edit_income(request, income_id):
    income = get_object_or_404(Transaction, id=income_id, user=request.user, transaction_type='INCOME')
    if request.method == 'POST':
        # Get form data
        amount = request.POST.get('amount')
        category_id = request.POST.get('category')
        date = request.POST.get('date')
        description = request.POST.get('description')
        is_recurring = request.POST.get('is_recurring') == 'on'
        recurrence_frequency = request.POST.get('recurrence_frequency')
        payment_method = request.POST.get('payment_method')

        # Validate and update the income
        if amount and category_id and date:
            category = Category.objects.get(id=category_id)
            income.amount = amount
            income.category = category
            income.date = date
            income.description = description
            income.is_recurring = is_recurring
            income.recurrence_frequency = recurrence_frequency
            income.payment_method = payment_method
            income.save()
            messages.success(request, 'Income updated successfully!')
            return redirect('income')
        else:
            messages.error(request, 'Please fill out all required fields.')
    else:
        # Fetch all categories for the dropdown
        categories = Category.objects.filter(user=request.user) | Category.objects.filter(is_default=True)
    return render(request, 'income/edit_income.html', {'income': income, 'categories': categories})

@login_required
def delete_income(request, income_id):
    income = get_object_or_404(Transaction, id=income_id, user=request.user, transaction_type='INCOME')
    income.delete()
    messages.success(request, 'Income deleted successfully!')
    return redirect('income')


@login_required
def budget_list(request):
    budgets = Budget.objects.filter(user=request.user).order_by('category__name')
    
    # Calculate current spending for each budget
    for budget in budgets:
        current_spending = Transaction.objects.filter(
            user=request.user,
            category=budget.category,
            transaction_type='EXPENSE',
            date__range=[budget.start_date, budget.end_date]
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        budget.current_spending = current_spending
        budget.percentage_used = (current_spending / budget.amount) * 100

    return render(request, 'budget/budgets.html', {'budgets': budgets})

@login_required
def add_budget(request):
    if request.method == 'POST':
        category_id = request.POST.get('category')
        amount = request.POST.get('amount')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        alert_threshold = request.POST.get('alert_threshold', 80)

        Budget.objects.create(
            user=request.user,
            category_id=category_id,
            amount=amount,
            start_date=start_date,
            end_date=end_date,
            alert_threshold=alert_threshold
        )

        return redirect('budgets')

    categories = Category.objects.filter(user=request.user) | Category.objects.filter(is_default=True)
    return render(request, 'budget/add_budget.html', {'categories': categories})

@login_required
def categories(request):
    # Fetch all categories for the logged-in user
    user_categories = Category.objects.filter(user=request.user)
    default_categories = Category.objects.filter(is_default=True)
    categories = user_categories | default_categories
    return render(request, 'categories/categories.html', {'categories': categories})

@login_required
def add_category(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        parent_id = request.POST.get('parent')
        parent = Category.objects.get(id=parent_id) if parent_id else None

        # Create the category
        Category.objects.create(
            name=name,
            user=request.user,
            parent=parent
        )
        messages.success(request, 'Category added successfully!')
        return redirect('categories')
    else:
        # Fetch all categories for the parent dropdown
        categories = Category.objects.filter(user=request.user)
        return render(request, 'categories/add_category.html', {'categories': categories})

@login_required
def edit_category(request, category_id):
    category = get_object_or_404(Category, id=category_id, user=request.user)
    if request.method == 'POST':
        name = request.POST.get('name')
        parent_id = request.POST.get('parent')
        parent = Category.objects.get(id=parent_id) if parent_id else None

        # Update the category
        category.name = name
        category.parent = parent
        category.save()
        messages.success(request, 'Category updated successfully!')
        return redirect('categories')
    else:
        # Fetch all categories for the parent dropdown
        categories = Category.objects.filter(user=request.user).exclude(id=category_id)
        return render(request, 'categories/edit_category.html', {'category': category, 'categories': categories})

@login_required
def delete_category(request, category_id):
    category = get_object_or_404(Category, id=category_id, user=request.user)
    category.delete()
    messages.success(request, 'Category deleted successfully!')
    return redirect('categories')

@login_required
def goals(request):
    # Fetch all goals for the logged-in user
    user_goals = Goal.objects.filter(user=request.user)
    return render(request, 'goal/goals.html', {'goals': user_goals})

@login_required
def add_goal(request):
    if request.method == 'POST':
        # Get form data
        name = request.POST.get('name')
        goal_type = request.POST.get('goal_type')
        target_amount = request.POST.get('target_amount')
        deadline = request.POST.get('deadline')

        # Validate and save the goal
        if name and goal_type and target_amount and deadline:
            Goal.objects.create(
                user=request.user,
                name=name,
                goal_type=goal_type,
                target_amount=target_amount,
                deadline=deadline
            )
            messages.success(request, 'Goal added successfully!')
            return redirect('goals')
        else:
            messages.error(request, 'Please fill out all required fields.')
    return render(request, 'goal/add_goal.html')

@login_required
def edit_goal(request, goal_id):
    goal = get_object_or_404(Goal, id=goal_id, user=request.user)
    if request.method == 'POST':
        # Get form data
        name = request.POST.get('name')
        goal_type = request.POST.get('goal_type')
        target_amount = request.POST.get('target_amount')
        deadline = request.POST.get('deadline')

        # Validate and update the goal
        if name and goal_type and target_amount and deadline:
            goal.name = name
            goal.goal_type = goal_type
            goal.target_amount = target_amount
            goal.deadline = deadline
            goal.save()
            messages.success(request, 'Goal updated successfully!')
            return redirect('goals')
        else:
            messages.error(request, 'Please fill out all required fields.')
    return render(request, 'goal/edit_goal.html', {'goal': goal})

@login_required
def delete_goal(request, goal_id):
    goal = get_object_or_404(Goal, id=goal_id, user=request.user)
    goal.delete()
    messages.success(request, 'Goal deleted successfully!')
    return redirect('goals')

@login_required
def profile(request):
    if request.method == 'POST':
        request.user.profile.currency = request.POST.get('currency')
        request.user.profile.monthly_income = request.POST.get('monthly_income')
        request.user.profile.savings_target = request.POST.get('savings_target')
        request.user.profile.save()
        return redirect('profile')

    return render(request, 'dashboard/profile.html')

@login_required
def reports(request):
    # Fetch all reports for the logged-in user
    user_reports = Report.objects.filter(user=request.user)
    return render(request, 'report/reports.html', {'reports': user_reports})

@login_required
def generate_report(request):
    if request.method == 'POST':
        # Get form data
        report_type = request.POST.get('report_type')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        category_ids = request.POST.getlist('categories')

        # Validate and generate the report
        if report_type and start_date and end_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

            # Fetch transactions based on filters
            transactions = Transaction.objects.filter(
                user=request.user,
                date__range=[start_date, end_date]
            )
            if category_ids:
                transactions = transactions.filter(category__id__in=category_ids)

            # Prepare report data
            report_data = {
                'report_type': report_type,
                'start_date': start_date.strftime('%Y-%m-%d'),  # Convert date to string
                'end_date': end_date.strftime('%Y-%m-%d'),      # Convert date to string
                'transactions': [
                    {
                        'date': transaction.date.strftime('%Y-%m-%d'),  # Convert date to string
                        'amount': str(transaction.amount),              # Convert Decimal to string
                        'category__name': transaction.category.name,
                        'transaction_type': transaction.transaction_type
                    }
                    for transaction in transactions
                ]
            }

            # Save the report
            report = Report.objects.create(
                user=request.user,
                report_type=report_type,
                generated_at=datetime.now(),
                data=report_data
            )
            messages.success(request, 'Report generated successfully!')
            return redirect('report_detail', report_id=report.id)
        else:
            messages.error(request, 'Please fill out all required fields.')
    else:
        # Fetch all categories for the dropdown
        categories = Category.objects.filter(user=request.user) | Category.objects.filter(is_default=True)
    return render(request, 'report/generate_report.html', {'categories': categories})

@login_required
def report_detail(request, report_id):
    # Fetch the report
    report = get_object_or_404(Report, id=report_id, user=request.user)
    return render(request, 'report/report_detail.html', {'report': report})

@login_required
def download_report(request, report_id):
    # Fetch the report
    report = get_object_or_404(Report, id=report_id, user=request.user)

    # Prepare the report data for download (e.g., as JSON)
    response = JsonResponse(report.data, safe=False)
    response['Content-Disposition'] = f'attachment; filename="report_{report.id}.json"'
    return response

@login_required
def settings(request):
    return render(request, 'setting/settings.html')