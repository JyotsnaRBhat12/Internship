import mysql.connector
import csv

db_config = {
    'host': 'localhost',
    'user': 'root',         
    'password': 'Jyotsna', 
    'database': 'student_db'
}

def get_connection():
    return mysql.connector.connect(**db_config)

def add_student(name, age, grade, email):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO students (name, age, grade, email) VALUES (%s, %s, %s, %s)", (name, age, grade, email))
    conn.commit()
    print(" Student added successfully!!!")
    conn.close()

def view_students():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students")
    for row in cursor.fetchall():
        print(row)
    conn.close()

def update_student(s_id, field, new_value):
    conn = get_connection()
    cursor = conn.cursor()
    query = f"UPDATE students SET {field} = %s WHERE id = %s"
    cursor.execute(query, (new_value, s_id))
    conn.commit()
    print("Record updated!!!")
    conn.close()

def delete_student(s_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM students WHERE id = %s", (s_id,))
    conn.commit()
    print(" Record deleted!!!")
    conn.close()

def search_students(criteria, value):
    conn = get_connection()
    cursor = conn.cursor()
    query = f"SELECT * FROM students WHERE {criteria} LIKE %s"
    cursor.execute(query, (f"%{value}%",))
    results = cursor.fetchall()
    
    if results:
        for row in results:
            print(row)
    else:
        print("No matching student found!")
    
    conn.close()

def export_to_csv():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students")
    rows = cursor.fetchall()
    
    with open('students_export.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['ID', 'Name', 'Age', 'Grade', 'Email']) 
        writer.writerows(rows)
    print(" Exported to students_export.csv")
    conn.close()

def main():
    while True:
        print("\n--- Student Management System ---")
        print("1. Add | 2. View | 3. Update | 4. Delete | 5. Search | 6. Export | 7. Exit")
        choice = input("Select an option: ")

        if choice == '1':
            add_student(input("Name: "), input("Age: "), input("Grade: "), input("Email: "))
        elif choice == '2':
            view_students()
        elif choice == '3':
            update_student(input("ID: "), input("Field (name/grade/email): "), input("New Value: "))
        elif choice == '4':
            delete_student(input("ID to delete: "))
        elif choice == '5':
            crit = input("Search by (name/grade/id): ")
            val = input("Value: ")
            search_students(crit, val)
        elif choice == '6':
            export_to_csv()
        elif choice == '7':
            break

if __name__ == "__main__":
    main()