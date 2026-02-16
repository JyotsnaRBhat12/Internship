import csv
from datetime import datetime, timedelta

class Book:
    def __init__(self, book_id, title, author, available=True):
        self.book_id = book_id
        self.title = title
        self.author = author
        self.available = available

class Member:
    def __init__(self, member_id, name):
        self.member_id = member_id
        self.name = name

class Transaction:
    LATE_FEE_PER_DAY = 10

    def __init__(self, book_id, member_id, borrow_date, due_date, return_date=""):
        self.book_id = book_id
        self.member_id = member_id
        self.borrow_date = borrow_date
        self.due_date = due_date
        self.return_date = return_date

def read_csv(filename):
    try:
        with open(filename, 'r', newline='') as file:
            return list(csv.reader(file))
    except FileNotFoundError:
        return []


def write_csv(filename, data):
    try:
        with open(filename, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(data)
    except Exception as e:
        print("Error writing file:", e)


def borrow_book():
    book_id = input("Enter Book ID: ")
    member_id = input("Enter Member ID: ")

    books = read_csv("books.csv")
    for book in books:
        if book[0] == book_id and book[3] == "True":
            book[3] = "False"

            borrow_date = datetime.now().date()
            due_date = borrow_date + timedelta(days=7)

            transactions = read_csv("transactions.csv")
            transactions.append([book_id,member_id,borrow_date,due_date,""])

            write_csv("books.csv", books)
            write_csv("transactions.csv", transactions)
            print("Book borrowed successfully!")
            return

    print("Book not available or invalid ID.")


def return_book():
    book_id = input("Enter Book ID: ")

    transactions = read_csv("transactions.csv")
    for t in transactions:
        if t[0] == book_id and t[4] == "":
            return_date = datetime.now().date()
            due_date = datetime.strptime(t[3], "%Y-%m-%d").date()

            late_days = (return_date - due_date).days
            late_fee = max(0, late_days * Transaction.LATE_FEE_PER_DAY)

            t[4] = return_date

            books = read_csv("books.csv")
            for book in books:
                if book[0] == book_id:
                    book[3] = "True"

            write_csv("books.csv", books)
            write_csv("transactions.csv", transactions)

            print("Book returned successfully!")
            print("Late Fee: Rs.", late_fee)
            return

    print("Transaction not found.")


def menu():
    while True:
        print("\n--- Library Management System ---")
        print("1. Borrow Book")
        print("2. Return Book")
        print("3. Exit")

        try:
            choice = int(input("Enter choice: "))
            if choice == 1:
                borrow_book()
            elif choice == 2:
                return_book()
            elif choice == 3:
                print("Exiting...")
                break
            else:
                print("Invalid choice!")
        except ValueError:
            print("Please enter a number.")

def setup_files():
    if not read_csv("books.csv"):
        write_csv("books.csv", [
            ["B1", "Python Basics", "Guido", "True"],
            ["B2", "Data Science", "Smith", "True"],
            ["B3", "Machine Learning", "Andrew Ng", "True"],
            ["B4", "Database Systems", "Elmasri", "True"],
            ["B5", "Operating Systems", "Galvin", "True"]
        ])

    if not read_csv("members.csv"):
        write_csv("members.csv", [
            ["M1", "Anu"],
            ["M2", "Ravi"],
            ["M3", "Sneha"],
            ["M4", "Arjun"],
            ["M5", "Meera"]
        ])

    if not read_csv("transactions.csv"):
        write_csv("transactions.csv", [])

setup_files()
menu()
