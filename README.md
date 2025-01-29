# Financial Planner Web App

<!-- ![Financial Planner Screenshot](screenshot.png) -->

The **Financial Planner** is a powerful web application designed to help users manage their finances effectively. It allows users to track expenses, set budgets, define financial goals, and generate insightful reports. Built with **Django** and **Tailwind CSS**, this app provides a clean, responsive, and user-friendly interface.

---

## Features

### 1. **Expense Tracking**
   - Add, edit, or delete expenses.
   - Categorize expenses (e.g., groceries, utilities, entertainment).
   - Upload transaction files (CSV, bank statements) for bulk expense tracking.

### 2. **Budget Management**
   - Set monthly budgets for different categories.
   - Receive budget suggestions based on historical spending.
   - Get alerts when you're close to exceeding your budget.

### 3. **Goal Tracking**
   - Set financial goals (e.g., save for a vacation, pay off debt).
   - Track progress with visual indicators.
   - Calculate monthly savings required to achieve goals.

### 4. **Reports and Insights**
   - View detailed reports on spending, budgets, and goals.
   - Generate monthly summaries and trend analysis.
   - Export reports as PDF or CSV.

### 5. **User Authentication**
   - Secure user accounts with email and password.
   - Password reset functionality.

### 6. **Responsive Design**
   - Built with **Tailwind CSS** for a modern and responsive UI.
   - Works seamlessly on desktop, tablet, and mobile devices.

---

## Tech Stack

- **Frontend**: HTML, Tailwind CSS, JavaScript, Chart.js
- **Backend**: Django (Python)
- **Database**: MySQL
- **Version Control**: Git

---

## Installation

### Prerequisites
- Python 3.8 or higher
- Pip (Python package manager)
- Git

### Steps

1. **Clone the Repository**
   ```bash
   git clone https://github.com/your-username/financial-planner.git
   cd financial-planner
   python -m venv venv
   ```
2. **Set Up a Virtual Environment**
   ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. **Install Dependencies**
   ```bash
    pip install -r requirements.txt
   ```
4. **Run the Development Server**
   ```bash
    python manage.py runserver
   ```
5. **Access the App**
   Open your browser and go to http://127.0.0.1:8000/