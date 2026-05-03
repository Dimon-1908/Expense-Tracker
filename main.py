import tkinter as tk
from tkinter import ttk, messagebox
import json
from datetime import datetime
import os

class ExpenseTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Expense Tracker")
        self.root.geometry("900x600")

        self.expenses = []
        self.load_data()

        self.create_widgets()

    def create_widgets(self):
        # Форма ввода
        input_frame = ttk.LabelFrame(self.root, text="Добавить расход")
        input_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(input_frame, text="Сумма:").grid(row=0, column=0, padx=5, pady=5)
        self.amount_entry = ttk.Entry(input_frame)
        self.amount_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(input_frame, text="Категория:").grid(row=0, column=2, padx=5, pady=5)
        self.category_var = tk.StringVar()
        self.category_combo = ttk.Combobox(
            input_frame,
            textvariable=self.category_var,
            values=["Еда", "Транспорт", "Развлечения", "Жильё", "Прочее"]
        )
        self.category_combo.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(input_frame, text="Дата (ГГГГ-ММ-ДД):").grid(row=1, column=0, padx=5, pady=5)
        self.date_entry = ttk.Entry(input_frame)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.date_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Button(input_frame, text="Добавить расход", command=self.add_expense).grid(
            row=1, column=2, columnspan=2, padx=5, pady=5
        )

        # Таблица
        table_frame = ttk.LabelFrame(self.root, text="Список расходов")
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)

        columns = ("ID", "Сумма", "Категория", "Дата")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)
        self.tree.pack(fill="both", expand=True)

        # Фильтры
        filter_frame = ttk.LabelFrame(self.root, text="Фильтры")
        filter_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(filter_frame, text="Категория:").grid(row=0, column=0, padx=5, pady=5)
        self.filter_category = ttk.Combobox(filter_frame, values=["Все"] + ["Еда", "Транспорт", "Развлечения", "Жильё", "Прочее"])
        self.filter_category.set("Все")
        self.filter_category.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(filter_frame, text="С даты:").grid(row=0, column=2, padx=5, pady=5)
        self.from_date = ttk.Entry(filter_frame)
        self.from_date.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(filter_frame, text="По дату:").grid(row=0, column=4, padx=5, pady=5)
        self.to_date = ttk.Entry(filter_frame)
        self.to_date.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.to_date.grid(row=0, column=5, padx=5, pady=5)

        ttk.Button(filter_frame, text="Применить фильтры", command=self.apply_filters).grid(
            row=0, column=6, padx=5, pady=5
        )

        # Итог
        self.total_label = ttk.Label(self.root, text="Общая сумма: 0 руб.")
        self.total_label.pack(pady=5)

        self.update_table()

    def add_expense(self):
        try:
            amount = float(self.amount_entry.get())
            if amount <= 0:
                messagebox.showerror("Ошибка", "Сумма должна быть положительным числом")
                return

            category = self.category_var.get()
            if not category:
                messagebox.showerror("Ошибка", "Выберите категорию")
                return

            date_str = self.date_entry.get()
            try:
                datetime.strptime(date_str, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Ошибка", "Неверный формат даты. Используйте ГГГГ-ММ-ДД")
                return

            expense = {
                "id": len(self.expenses) + 1,
                "amount": amount,
                "category": category,
                "date": date_str
            }
            self.expenses.append(expense)
            self.update_table()
            self.save_data()
            self.clear_form()
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректную сумму")

    def update_table(self, expenses=None):
        for item in self.tree.get_children():
            self.tree.delete(item)

        if expenses is None:
            expenses = self.expenses


        total = 0
        for expense in expenses:
            self.tree.insert("", "end", values=(
                expense["id"],
                f"{expense['amount']} руб.",
                expense["category"],
                expense["date"]
            ))
            total += expense["amount"]

        self.total_label.config(text=f"Общая сумма: {total} руб.")

    def apply_filters(self):
        filtered = self.expenses
        category = self.filter_category.get()
        if category != "Все":
            filtered = [e for e in filtered if e["category"] == category]

        from_date_str = self.from_date.get()
        to_date_str = self.to_date.get()

        if from_date_str:
            try:
                from_date = datetime.strptime(from_date_str, "%Y-%m-%d")
                filtered = [e for e in filtered if datetime.strptime(e["date"], "%Y-%m-%d") >= from_date]
            except ValueError:
                messagebox.showerror("Ошибка", "Неверный формат начальной даты")
                return

        if to_date_str:
            try:
                to_date = datetime.strptime(to_date_str, "%Y-%m-%d")
                filtered = [e for e in filtered if datetime.strptime(e["date"], "%Y-%m-%d") <= to_date]
            except ValueError:
                messagebox.showerror("Ошибка", "Неверный формат конечной даты")
                return

        self.update_table(filtered)

    def clear_form(self):
        self.amount_entry.delete(0, tk.END)
        self.category_combo.set("")
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

    def save_data(self):
        with open("expenses.json", "w", encoding="utf-8") as f:
            json.dump(self.expenses, f, ensure_ascii=False, indent=2)


    def load_data(self):
        if os.path.exists("expenses.json"):
            try:
                with open("expenses.json", "r", encoding="utf-8") as f:
                    self.expenses = json.load(f)
            except (json.JSONDecodeError, IOError):
                self.expenses = []
        else:
            self.expenses = []
        # Запуск приложения
if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTracker(root)
    root.mainloop()