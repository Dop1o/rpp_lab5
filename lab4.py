import os
import csv
from datetime import datetime

class Transaction:
    _all = []  # Для итератора

    def __init__(self, id, date, amount, desc):
        self.id = id
        self.date = date
        self.amount = amount
        self.desc = desc
        Transaction._all.append(self)

    def __setattr__(self, name, value):
        if name == "amount" and value < 0:
            raise ValueError("Сумма не может быть отрицательной")
        super().__setattr__(name, value)

    def __repr__(self):
        return f"Transaction({self.id}, {self.date}, {self.amount}, {self.desc})"

    @staticmethod
    def is_large(amount):
        return amount > 10000

    @classmethod
    def all_transactions(cls):
        for t in cls._all:
            yield t

    @classmethod
    def iterator(cls):
        return iter(cls._all)


class LargeTransaction(Transaction):
    def __init__(self, id, date, amount, desc, risk="средний"):
        super().__init__(id, date, amount, desc)
        self.risk = risk

    def __repr__(self):
        return f"LargeTransaction({self.id}, {self.amount}, risk={self.risk})"


class TransactionCollection:
    def __init__(self):
        self._items = []

    def add(self, t):
        self._items.append(t)

    def __getitem__(self, i):
        return self._items[i]

    def __len__(self):
        return len(self._items)

    def __repr__(self):
        return f"Collection({len(self._items)})"

    def sort_by_desc(self):
        return sorted(self._items, key=lambda x: x.desc)

    def sort_by_amount(self):
        return sorted(self._items, key=lambda x: x.amount)

    def filter(self, min_amount):
        return [t for t in self._items if t.amount > min_amount]

    def large_gen(self):
        for t in self._items:
            if t.amount > 10000:
                yield t

    def save(self, fname):
        with open(fname, 'w', encoding='utf-8', newline='') as f:
            w = csv.DictWriter(f, fieldnames=['id','date','amount','desc'])
            w.writeheader()
            for t in self._items:
                w.writerow({'id': t.id, 'date': t.date, 'amount': t.amount, 'desc': t.desc})

    def load(self, fname):
        try:
            with open(fname, 'r', encoding='utf-8') as f:
                for row in csv.DictReader(f):
                    data = {'id': int(row['id']), 'date': row['date'], 
                           'amount': float(row['amount']), 'desc': row['desc']}
                    if data['amount'] > 50000:
                        self.add(LargeTransaction(**data))
                    else:
                        self.add(Transaction(**data))
            return True
        except:
            return False


def main():
    print("=" * 60)
    print("ЛАБОРАТОРНАЯ РАБОТА №4 (Вариант 4)")
    print("=" * 60)

    # 1. Счет файлов
    files = [f for f in os.listdir('.') if os.path.isfile(f)]
    print(f"\n1. Файлов в папке: {len(files)}")

    # 2. Загрузка данных
    col = TransactionCollection()
    if not col.load("data.csv"):
        print("Создаем тестовые данные...")
        test = [
            {'id': 1, 'date': '2026-01-15 10:30', 'amount': 1500.50, 'desc': 'Другу'},
            {'id': 2, 'date': '2026-01-16 14:45', 'amount': 3200.00, 'desc': 'Коммуналка'},
            {'id': 3, 'date': '2026-01-17 09:15', 'amount': 500.75, 'desc': 'Кофе'},
            {'id': 4, 'date': '2026-02-01 11:20', 'amount': 75000.00, 'desc': 'Машина'},
        ]
        for d in test:
            col.add(LargeTransaction(**d) if d['amount'] > 50000 else Transaction(**d))

    print(f"Загружено транзакций: {len(col)}")

    # 3. Демонстрация всех требований
    print("\n" + "=" * 60)
    print("ДЕМОНСТРАЦИЯ ТРЕБОВАНИЙ")
    print("=" * 60)

    # п.1 Итератор
    print("\n1. Итератор:")
    for t in Transaction.iterator():
        print(f"  - {t.id}: {t.amount}")

    # п.2 repr
    print("\n2. repr:")
    print(f"  {repr(col)}")
    if len(col) > 0:
        print(f"  {repr(col[0])}")

    # п.3 Наследование
    print("\n3. Наследование:")
    for t in col._items:
        if isinstance(t, LargeTransaction):
            print(f"  Крупная: {t}")

    # п.4 __setattr__
    print("\n4. __setattr__:")
    try:
        Transaction(5, "now", 100, "test")
    except ValueError as e:
        print(f"  Ошибка: {e}")

    # п.5 __getitem__
    print("\n5. Доступ по индексу:")
    if len(col) > 2:
        print(f"  Первая: {col[0].id}")
        print(f"  Вторая: {col[1].id}")

    # п.6 Статический метод
    print("\n6. Статический метод:")
    print(f"  15000 крупная? {Transaction.is_large(15000)}")
    print(f"  5000 крупная? {Transaction.is_large(5000)}")

    # п.7 Генераторы
    print("\n7. Генераторы:")
    print("  Все транзакции:")
    for t in Transaction.all_transactions():
        print(f"    - {t.desc}")
    print("  Крупные (>10000):")
    for t in col.large_gen():
        print(f"    - {t.amount}")

    # 4. Сортировки и фильтры
    print("\n" + "=" * 60)
    print("СОРТИРОВКИ И ФИЛЬТРЫ")
    print("=" * 60)

    print("\nПо описанию:")
    for t in col.sort_by_desc()[:3]:
        print(f"  {t.desc}")

    print("\nПо сумме:")
    for t in col.sort_by_amount()[:3]:
        print(f"  {t.amount}")

    print("\nСумма > 2000:")
    for t in col.filter(2000):
        print(f"  {t.amount} - {t.desc}")

    # 5. Добавление и сохранение
    print("\n" + "=" * 60)
    print("ДОБАВЛЕНИЕ И СОХРАНЕНИЕ")
    print("=" * 60)

    try:
        new_id = max(t.id for t in col._items) + 1
        date = input("\nДата (ГГГГ-ММ-ДД ЧЧ:ММ) [Enter=сейчас]: ") or datetime.now().strftime("%Y-%m-%d %H:%M")
        amt = float(input("Сумма: ") or 1000)
        desc = input("Описание: ") or "Новая"

        if amt > 50000:
            t = LargeTransaction(new_id, date, amt, desc)
        else:
            t = Transaction(new_id, date, amt, desc)

        col.add(t)
        col.save("data.csv")
        print(f"Добавлено и сохранено в data.csv")
    except Exception as e:
        print(f"Ошибка: {e}")

    print("\n" + "=" * 60)
    print(f"ВСЕГО ТРАНЗАКЦИЙ: {len(col)}")
    print("=" * 60)


if __name__ == "__main__":
    main()