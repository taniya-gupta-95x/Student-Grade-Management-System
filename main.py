"""
Advanced Student Grade Management System
- Persistent storage using JSON
- Add / Update / Delete / View / Search / Sort
- Statistics: count, average, min, max, median
- Export / Import CSV
- Performance evaluation labels
- Optional colorama & tabulate for nicer CLI
"""

import json
import csv
import os
from statistics import mean, median
from datetime import datetime

# Optional libs (graceful fallback)
try:
    from colorama import Fore, Style, init as _colorama_init
    _colorama_init(autoreset=True)
    HAS_COLOR = True
except Exception:
    HAS_COLOR = False

try:
    from tabulate import tabulate
    HAS_TABULATE = True
except Exception:
    HAS_TABULATE = False

DATA_FILE = "grades_data.json"
AUTO_SAVE_ON_EXIT = True

# Utility helpers
def colored(text, color="green"):
    if not HAS_COLOR:
        return str(text)
    colors = {
        "green": Fore.GREEN,
        "red": Fore.RED,
        "yellow": Fore.YELLOW,
        "cyan": Fore.CYAN,
        "magenta": Fore.MAGENTA
    }
    return colors.get(color, Fore.GREEN) + str(text) + Style.RESET_ALL

def safe_input(prompt=""):
    try:
        return input(prompt)
    except (KeyboardInterrupt, EOFError):
        print()
        return ""

# Data store and functions
student_grades = {}  # { "Name": grade_float }

def load_data(filename=DATA_FILE):
    global student_grades
    if os.path.exists(filename):
        try:
            with open(filename, "r", encoding="utf-8") as f:
                student_grades = json.load(f)
            # convert grades to float (in case stored as ints/strings)
            student_grades = {k: float(v) for k, v in student_grades.items()}
            print(colored(f"✅ Loaded {len(student_grades)} records from {filename}", "cyan"))
        except Exception as e:
            print(colored(f"Failed to load data: {e}", "yellow"))
    else:
        print(colored("No existing data file found. Starting fresh.", "yellow"))

def save_data(filename=DATA_FILE):
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(student_grades, f, indent=4)
        print(colored(f"Data saved to {filename}", "green"))
    except Exception as e:
        print(colored(f"Failed to save data: {e}", "red"))

def validate_name(name):
    if not name or not name.strip():
        return False
    return True

def validate_grade(grade):
    try:
        g = float(grade)
        if 0.0 <= g <= 100.0:
            return True
        return False
    except Exception:
        return False

def evaluate_performance(grade):
    g = float(grade)
    if g >= 90:
        return "Excellent"
    if g >= 75:
        return "Good"
    if g >= 50:
        return "Average"
    return "Needs Improvement"

# CRUD + features
def add_student(name, grade):
    name = name.strip()
    if not validate_name(name):
        print(colored("Invalid name. Try again.", "yellow"))
        return
    if not validate_grade(grade):
        print(colored("Invalid grade. Enter a number between 0 and 100.", "yellow"))
        return
    student_grades[name] = float(grade)
    print(colored(f"Added {name} with grade {grade}. Performance: {evaluate_performance(grade)}", "green"))

def update_student(name, grade):
    name = name.strip()
    if name not in student_grades:
        print(colored(f"{name} not found.", "yellow"))
        return
    if not validate_grade(grade):
        print(colored("Invalid grade. Enter a number between 0 and 100.", "yellow"))
        return
    student_grades[name] = float(grade)
    print(colored(f"Updated {name} to grade {grade}. Performance: {evaluate_performance(grade)}", "cyan"))

def delete_student(name):
    name = name.strip()
    if name in student_grades:
        del student_grades[name]
        print(colored(f"Deleted {name}.", "green"))
    else:
        print(colored(f"{name} not found.", "yellow"))

def display_all_students(sorted_by=None, reverse=False):
    if not student_grades:
        print(colored("No students found.", "yellow"))
        return
    rows = []
    for name, grade in student_grades.items():
        rows.append([name, float(grade), evaluate_performance(grade)])
    if sorted_by == "name":
        rows.sort(key=lambda x: x[0], reverse=reverse)
    elif sorted_by == "grade":
        rows.sort(key=lambda x: x[1], reverse=reverse)
    headers = ["Name", "Grade", "Performance"]
    if HAS_TABULATE:
        print(tabulate(rows, headers=headers, tablefmt="grid", floatfmt=".2f"))
    else:
        print(f"{headers[0]:<25} {headers[1]:<8} {headers[2]}")
        print("-" * 45)
        for r in rows:
            print(f"{r[0]:<25} {r[1]:<8.2f} {r[2]}")

def search_student(query):
    query = query.strip().lower()
    results = {name:grade for name, grade in student_grades.items() if query in name.lower()}
    if not results:
        print(colored("No matching students found.", "yellow"))
        return
    print(colored(f"Found {len(results)} result(s):", "cyan"))
    for name, grade in results.items():
        print(f"- {name}: {grade} ({evaluate_performance(grade)})")

def sort_and_display(by="grade", top_n=None, reverse=True):
    if not student_grades:
        print(colored("No students to show.", "yellow"))
        return
    if by == "grade":
        sorted_list = sorted(student_grades.items(), key=lambda x: x[1], reverse=reverse)
    else:
        sorted_list = sorted(student_grades.items(), key=lambda x: x[0], reverse=reverse)
    if top_n:
        sorted_list = sorted_list[:top_n]
    rows = [[name, grade, evaluate_performance(grade)] for name, grade in sorted_list]
    headers = ["Name", "Grade", "Performance"]
    if HAS_TABULATE:
        print(tabulate(rows, headers=headers, tablefmt="fancy_grid", floatfmt=".2f"))
    else:
        for r in rows:
            print(f"{r[0]:<25} {r[1]:<8.2f} {r[2]}")

# Statistics & Reports
def show_statistics():
    if not student_grades:
        print(colored("No data to calculate statistics.", "yellow"))
        return
    grades = list(student_grades.values())
    total = len(grades)
    avg = mean(grades)
    med = median(grades)
    mx = max(grades)
    mn = min(grades)
    print(colored("Grade Statistics", "magenta"))
    print(f"Total Students : {total}")
    print(f"Average Grade  : {avg:.2f}")
    print(f"Median Grade   : {med:.2f}")
    print(f"Highest Grade  : {mx:.2f}")
    print(f"Lowest Grade   : {mn:.2f}")

# CSV Export / Import
def export_csv(filename="grades_export.csv"):
    try:
        with open(filename, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Name", "Grade"])
            for name, grade in student_grades.items():
                writer.writerow([name, grade])
        print(colored(f"Exported data to {filename}", "green"))
    except Exception as e:
        print(colored(f"Export failed: {e}", "red"))

def import_csv(filename):
    if not os.path.exists(filename):
        print(colored("CSV file not found.", "yellow"))
        return
    try:
        count = 0
        with open(filename, "r", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                name = row.get("Name") or row.get("name")
                grade = row.get("Grade") or row.get("grade")
                if name and validate_grade(grade):
                    student_grades[name.strip()] = float(grade)
                    count += 1
        print(colored(f"Imported {count} records from {filename}", "green"))
    except Exception as e:
        print(colored(f"Import failed: {e}", "red"))

# Menu / CLI
def print_menu():
    print("\n" + colored("=============================================", "magenta"))
    print(colored("Student Grade Management System", "magenta"))
    print(colored("=============================================", "magenta"))
    print("1. Add Student")
    print("2. Update Student")
    print("3. Delete Student")
    print("4. View All Students")
    print("5. Search Student")
    print("6. Sort & View (by grade/name)")
    print("7. View Statistics")
    print("8. Export to CSV")
    print("9. Import from CSV")
    print("10. Save Data")
    print("0. Exit")
    print(colored("=============================================", "magenta"))

def main():
    load_data()
    while True:
        print_menu()
        choice = safe_input("Enter choice: ").strip()
        if choice == "1":
            name = safe_input("Enter student name: ").strip()
            grade = safe_input("Enter grade (0-100): ").strip()
            add_student(name, grade)

        elif choice == "2":
            name = safe_input("Enter student name to update: ").strip()
            if name not in student_grades:
                print(colored("Student not found.", "yellow"))
                continue
            grade = safe_input(f"Enter new grade for {name} (0-100): ").strip()
            update_student(name, grade)

        elif choice == "3":
            name = safe_input("Enter student name to delete: ").strip()
            confirm = safe_input(f"Are you sure you want to delete '{name}'? (y/n): ").strip().lower()
            if confirm == "y":
                delete_student(name)
            else:
                print(colored("Delete cancelled.", "yellow"))

        elif choice == "4":
            # optional sorting prompt
            s = safe_input("Sort by (none/name/grade): ").strip().lower()
            if s == "name":
                display_all_students(sorted_by="name")
            elif s == "grade":
                display_all_students(sorted_by="grade", reverse=True)
            else:
                display_all_students()

        elif choice == "5":
            q = safe_input("Enter search text (name or part): ").strip()
            search_student(q)

        elif choice == "6":
            by = safe_input("Sort by (grade/name): ").strip().lower() or "grade"
            rev = safe_input("Reverse order? (y/n): ").strip().lower() == "y"
            top = safe_input("Top N? (press enter for all): ").strip()
            top_n = int(top) if top.isdigit() and int(top) > 0 else None
            sort_and_display(by="grade" if by=="grade" else "name", top_n=top_n, reverse=rev)

        elif choice == "7":
            show_statistics()

        elif choice == "8":
            fname = safe_input("Enter csv filename to export (default: grades_export.csv): ").strip() or "grades_export.csv"
            export_csv(fname)

        elif choice == "9":
            fname = safe_input("Enter csv filename to import: ").strip()
            if fname:
                import_csv(fname)

        elif choice == "10":
            save_data()

        elif choice == "0":
            if AUTO_SAVE_ON_EXIT:
                save_data()
            print(colored("Exiting. Good luck!", "cyan"))
            break

        else:
            print(colored("Invalid choice. Try again.", "yellow"))


if __name__ == "__main__":
    main()
