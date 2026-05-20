import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime

DATA_FILE = "expenses.json"

class ExpenseTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Expense Tracker")
        self.root.geometry("800x600")

        # Данные
        self.expenses = []
        self.categories = ["Еда", "Транспорт", "Развлечения", "Здоровье", "Счета", "Другое"]
        self.load_data()

        # Создание интерфейса
        self.create_widgets()
        self.refresh_table()

    def create_widgets(self):
        # Рамка для ввода данных
        input_frame = ttk.LabelFrame(self.root, text="Добавить расход", padding=10)
        input_frame.pack(fill="x", padx=10, pady=5)

        # Сумма
        ttk.Label(input_frame, text="Сумма:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.amount_entry = ttk.Entry(input_frame, width=20)
        self.amount_entry.grid(row=0, column=1, padx=5, pady=5)

        # Категория
        ttk.Label(input_frame, text="Категория:").grid(row=0, column=2, sticky="w", padx=5, pady=5)
        self.category_combo = ttk.Combobox(input_frame, values=self.categories, width=15)
        self.category_combo.grid(row=0, column=3, padx=5, pady=5)
        self.category_combo.current(0)

        # Дата
        ttk.Label(input_frame, text="Дата (ГГГГ-ММ-ДД):").grid(row=0, column=4, sticky="w", padx=5, pady=5)
        self.date_entry = ttk.Entry(input_frame, width=15)
        self.date_entry.grid(row=0, column=5, padx=5, pady=5)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

        # Кнопка добавления
        add_btn = ttk.Button(input_frame, text="Добавить расход", command=self.add_expense)
        add_btn.grid(row=0, column=6, padx=10, pady=5)

        # Рамка для фильтров
        filter_frame = ttk.LabelFrame(self.root, text="Фильтрация", padding=10)
        filter_frame.pack(fill="x", padx=10, pady=5)

        # Фильтр по категории
        ttk.Label(filter_frame, text="Категория:").grid(row=0, column=0, sticky="w", padx=5)
        self.filter_category = ttk.Combobox(filter_frame, values=["Все"] + self.categories, width=15)
        self.filter_category.grid(row=0, column=1, padx=5)
        self.filter_category.current(0)
        self.filter_category.bind("<<ComboboxSelected>>", lambda e: self.refresh_table())

        # Фильтр по дате (период)
        ttk.Label(filter_frame, text="Дата от (ГГГГ-ММ-ДД):").grid(row=0, column=2, sticky="w", padx=5)
        self.filter_date_from = ttk.Entry(filter_frame, width=12)
        self.filter_date_from.grid(row=0, column=3, padx=5)

        ttk.Label(filter_frame, text="до:").grid(row=0, column=4, padx=2)
        self.filter_date_to = ttk.Entry(filter_frame, width=12)
        self.filter_date_to.grid(row=0, column=5, padx=5)

        apply_filter_btn = ttk.Button(filter_frame, text="Применить фильтр", command=self.refresh_table)
        apply_filter_btn.grid(row=0, column=6, padx=10)

        reset_filter_btn = ttk.Button(filter_frame, text="Сбросить фильтры", command=self.reset_filters)
        reset_filter_btn.grid(row=0, column=7, padx=5)

        # Рамка для суммы за период
        sum_frame = ttk.LabelFrame(self.root, text="Сумма расходов за выбранный период", padding=10)
        sum_frame.pack(fill="x", padx=10, pady=5)

        self.total_label = ttk.Label(sum_frame, text="Общая сумма: 0.00", font=("Arial", 12, "bold"))
        self.total_label.pack()

        # Таблица расходов
        table_frame = ttk.Frame(self.root)
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)

        columns = ("ID", "Дата", "Категория", "Сумма")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Дата", text="Дата")
        self.tree.heading("Категория", text="Категория")
        self.tree.heading("Сумма", text="Сумма")

        self.tree.column("ID", width=50)
        self.tree.column("Дата", width=100)
        self.tree.column("Категория", width=150)
        self.tree.column("Сумма", width=100)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Кнопка удаления
        delete_btn = ttk.Button(self.root, text="Удалить выбранный расход", command=self.delete_expense)
        delete_btn.pack(pady=5)

    def add_expense(self):
        """Добавление нового расхода с проверкой ввода"""
        try:
            amount = float(self.amount_entry.get())
            if amount <= 0:
                messagebox.showerror("Ошибка", "Сумма должна быть положительным числом")
                return
        except ValueError:
            messagebox.showerror("Ошибка", "Сумма должна быть числом")
            return

        category = self.category_combo.get()
        date_str = self.date_entry.get()

        # Проверка формата даты
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Ошибка", "Неверный формат даты. Используйте ГГГГ-ММ-ДД")
            return

        # Создание записи
        new_id = max([e["id"] for e in self.expenses], default=0) + 1
        expense = {
            "id": new_id,
            "amount": amount,
            "category": category,
            "date": date_str
        }
        self.expenses.append(expense)
        self.save_data()
        self.refresh_table()

        # Очистка полей ввода
        self.amount_entry.delete(0, tk.END)
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

        messagebox.showinfo("Успех", "Расход добавлен")

    def delete_expense(self):
        """Удаление выбранного расхода"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите расход для удаления")
            return

        item = self.tree.item(selected[0])
        expense_id = int(item["values"][0])

        self.expenses = [e for e in self.expenses if e["id"] != expense_id]
        self.save_data()
        self.refresh_table()
        messagebox.showinfo("Успех", "Расход удалён")

    def refresh_table(self):
        """Обновление таблицы с учётом фильтров и подсчёт суммы"""
        # Очистка таблицы
        for row in self.tree.get_children():
            self.tree.delete(row)

        # Получение фильтров
        category_filter = self.filter_category.get()
        date_from = self.filter_date_from.get().strip()
        date_to = self.filter_date_to.get().strip()

        filtered_expenses = []
        total = 0.0

        for expense in self.expenses:
            # Фильтр по категории
            if category_filter != "Все" and expense["category"] != category_filter:
                continue

            # Фильтр по дате
            expense_date = datetime.strptime(expense["date"], "%Y-%m-%d")

            if date_from:
                try:
                    from_date = datetime.strptime(date_from, "%Y-%m-%d")
                    if expense_date < from_date:
                        continue
                except ValueError:
                    pass

            if date_to:
                try:
                    to_date = datetime.strptime(date_to, "%Y-%m-%d")
                    if expense_date > to_date:
                        continue
                except ValueError:
                    pass

            filtered_expenses.append(expense)
            total += expense["amount"]

        # Сортировка по дате
        filtered_expenses.sort(key=lambda x: x["date"])

        # Заполнение таблицы
        for expense in filtered_expenses:
            self.tree.insert("", tk.END, values=(
                expense["id"],
                expense["date"],
                expense["category"],
                f"{expense['amount']:.2f}"
            ))

        self.total_label.config(text=f"Общая сумма за период: {total:.2f}")

    def reset_filters(self):
        """Сброс всех фильтров"""
        self.filter_category.current(0)
        self.filter_date_from.delete(0, tk.END)
        self.filter_date_to.delete(0, tk.END)
        self.refresh_table()

    def save_data(self):
        """Сохранение данных в JSON"""
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(self.expenses, f, ensure_ascii=False, indent=4)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить данные: {e}")

    def load_data(self):
        """Загрузка данных из JSON с обработкой пустого/битого файла"""
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    # Проверяем, не пустой ли файл
                    content = f.read().strip()
                    if not content:
                        # Файл пуст, используем пустой список
                        self.expenses = []
                        return
                    
                    # Пробуем распарсить JSON
                    self.expenses = json.loads(content)
            except json.JSONDecodeError as e:
                # Если JSON повреждён, показываем предупреждение и начинаем с пустого списка
                messagebox.showwarning("Предупреждение", 
                                     f"Файл данных повреждён. Будет создан новый файл.\nОшибка: {e}")
                self.expenses = []
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить данные: {e}")
                self.expenses = []
        else:
            # Файла не существует, начинаем с пустого списка
            self.expenses = []

if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTracker(root)
    root.mainloop()