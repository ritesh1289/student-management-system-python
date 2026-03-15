import json
import os

# File to store student data
DATA_FILE = "students.json"

def load_students():
    """Load students from the JSON file."""
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, 'r') as file:
            return json.load(file)
    except json.JSONDecodeError:
        return []

def save_students(students):
    """Save students to the JSON file."""
    with open(DATA_FILE, 'w') as file:
        json.dump(students, file, indent=4)

def generate_id(students):
    """Generate a unique ID for a new student."""
    if not students:
        return 1001
    # Get the max ID from existing students and add 1
    last_id = max(student['id'] for student in students)
    return last_id + 1

def add_student(students):
    """Add a new student record."""
    print("\n--- Add New Student ---")
    name = input("Enter Student Name: ").strip()
    
    # Simple input validation for age
    while True:
        try:
            age = int(input("Enter Student Age: "))
            break
        except ValueError:
            print("Invalid input. Please enter a number for age.")

    grade = input("Enter Student Grade/Class: ").strip()
    
    student_id = generate_id(students)
    
    student = {
        'id': student_id,
        'name': name,
        'age': age,
        'grade': grade
    }
    
    students.append(student)
    save_students(students)
    print(f"\nSuccess! Student added with ID: {student_id}")

def view_students(students):
    """Display all students."""
    print("\n--- Student List ---")
    if not students:
        print("No students found.")
        return

    print(f"{'ID':<10} {'Name':<20} {'Age':<10} {'Grade':<10}")
    print("-" * 50)
    for s in students:
        print(f"{s['id']:<10} {s['name']:<20} {s['age']:<10} {s['grade']:<10}")
    print("-" * 50)

def search_student(students):
    """Search for a student by ID."""
    print("\n--- Search Student ---")
    try:
        search_id = int(input("Enter Student ID to search: "))
    except ValueError:
        print("Invalid ID format.")
        return

    found = False
    for s in students:
        if s['id'] == search_id:
            print(f"\nStudent Found:")
            print(f"ID: {s['id']}")
            print(f"Name: {s['name']}")
            print(f"Age: {s['age']}")
            print(f"Grade: {s['grade']}")
            found = True
            break
    
    if not found:
        print("Student not found.")

def update_student(students):
    """Update an existing student's details."""
    print("\n--- Update Student ---")
    try:
        search_id = int(input("Enter Student ID to update: "))
    except ValueError:
        print("Invalid ID format.")
        return

    for s in students:
        if s['id'] == search_id:
            print(f"Editing {s['name']} (Leave blank to keep current value)")
            
            new_name = input(f"Enter new Name ({s['name']}): ").strip()
            new_age = input(f"Enter new Age ({s['age']}): ").strip()
            new_grade = input(f"Enter new Grade ({s['grade']}): ").strip()

            if new_name:
                s['name'] = new_name
            if new_age:
                try:
                    s['age'] = int(new_age)
                except ValueError:
                    print("Invalid age. Keeping previous value.")
            if new_grade:
                s['grade'] = new_grade
            
            save_students(students)
            print("Student updated successfully!")
            return
    
    print("Student not found.")

def delete_student(students):
    """Delete a student record."""
    print("\n--- Delete Student ---")
    try:
        search_id = int(input("Enter Student ID to delete: "))
    except ValueError:
        print("Invalid ID format.")
        return

    for i, s in enumerate(students):
        if s['id'] == search_id:
            confirm = input(f"Are you sure you want to delete {s['name']}? (y/n): ").lower()
            if confirm == 'y':
                students.pop(i)
                save_students(students)
                print("Student deleted successfully!")
            else:
                print("Operation cancelled.")
            return
    
    print("Student not found.")

def main():
    """Main menu loop."""
    students = load_students()
    
    while True:
        print("\n============================")
        print("   STUDENT MANAGEMENT SYSTEM")
        print("============================")
        print("1. Add Student")
        print("2. View All Students")
        print("3. Search Student")
        print("4. Update Student")
        print("5. Delete Student")
        print("6. Exit")
        
        choice = input("\nEnter your choice (1-6): ")

        if choice == '1':
            add_student(students)
        elif choice == '2':
            view_students(students)
        elif choice == '3':
            search_student(students)
        elif choice == '4':
            update_student(students)
        elif choice == '5':
            delete_student(students)
        elif choice == '6':
            print("Exiting program. Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()