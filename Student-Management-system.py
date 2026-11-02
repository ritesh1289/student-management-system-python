
import streamlit as st
import pandas as pd
import plotly.express as px
import json
from pathlib import Path
from datetime import date

# =====================================
# 1. APPLICATION CONFIGURATION
# =====================================

st.set_page_config(
    page_title="Student Management System",
    page_icon="🎓",
    layout="wide"
)

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"

DATA_DIR.mkdir(exist_ok=True)

STUDENTS_FILE = DATA_DIR / "students.json"
ATTENDANCE_FILE = DATA_DIR / "attendance.json"
MARKS_FILE = DATA_DIR / "marks.json"


# =====================================
# 2. JSON DATABASE FUNCTIONS
# =====================================

def load_data(file_path):

    if not file_path.exists():
        save_data(file_path, [])
        return []

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        return data if isinstance(data, list) else []

    except (json.JSONDecodeError, OSError):
        return []


def save_data(file_path, data):

    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


students = load_data(STUDENTS_FILE)
attendance = load_data(ATTENDANCE_FILE)
marks = load_data(MARKS_FILE)


def generate_student_id():

    if not students:
        return 1001

    return max(int(s["id"]) for s in students) + 1


def find_student(student_id):

    for student in students:
        if int(student["id"]) == int(student_id):
            return student

    return None


def grade_calculator(score):

    if score >= 80:
        return "A"

    elif score >= 70:
        return "B"

    elif score >= 60:
        return "C"

    elif score >= 40:
        return "D"

    else:
        return "F"


# =====================================
# 3. SIDEBAR NAVIGATION
# =====================================

st.sidebar.title("🎓 Student Management")

menu = st.sidebar.radio(
    "MAIN MENU",
    [
        "Dashboard",
        "Add Student",
        "View Students",
        "Update Student",
        "Delete Student",
        "Attendance",
        "Marks & Grades",
        "Reports",
        "Backup & Restore"
    ]
)

st.sidebar.divider()
st.sidebar.info("Advanced Student Management System")


# =====================================
# 4. MAIN HEADER
# =====================================

st.title("🎓 Student Management System")

st.caption(
    "Manage student records, attendance, marks and academic reports."
)


# =====================================
# 5. DASHBOARD
# =====================================

if menu == "Dashboard":

    st.header("📊 Dashboard Overview")

    total_students = len(students)
    total_attendance = len(attendance)
    total_marks = len(marks)

    present = sum(
        1 for a in attendance
        if a["status"] == "Present"
    )

    attendance_percentage = (
        (present / total_attendance) * 100
        if total_attendance else 0
    )

    average_marks = (
        sum(float(m["marks"]) for m in marks) / total_marks
        if total_marks else 0
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Students", total_students)
    col2.metric("Attendance Records", total_attendance)
    col3.metric("Attendance Rate", f"{attendance_percentage:.1f}%")
    col4.metric("Average Marks", f"{average_marks:.1f}")

    st.divider()

    if students:

        st.subheader("👨‍🎓 Students by Class")

        class_data = pd.DataFrame(students)

        class_count = (
            class_data["class_name"]
            .value_counts()
            .reset_index()
        )

        class_count.columns = ["Class", "Students"]

        fig = px.bar(
            class_count,
            x="Class",
            y="Students",
            title="Class-wise Student Distribution"
        )

        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Recently Added Students")

        st.dataframe(
            pd.DataFrame(students[-5:]),
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info("No student records found. Add your first student.")


# =====================================
# 6. ADD STUDENT
# =====================================

elif menu == "Add Student":

    st.header("➕ Register New Student")

    with st.form("student_form"):

        col1, col2 = st.columns(2)

        name = col1.text_input("Student Full Name *")

        age = col2.number_input(
            "Age",
            min_value=3,
            max_value=100,
            value=18
        )

        col3, col4 = st.columns(2)

        class_name = col3.text_input("Class / Grade *")
        section = col4.text_input("Section")

        col5, col6 = st.columns(2)

        email = col5.text_input("Email")
        phone = col6.text_input("Phone Number")

        gender = st.selectbox(
            "Gender",
            ["Prefer not to say", "Male", "Female", "Other"]
        )

        address = st.text_area("Address")

        submit = st.form_submit_button(
            "Register Student",
            type="primary"
        )

        if submit:

            if not name.strip() or not class_name.strip():

                st.error("Name and Class are required.")

            elif email.strip() and (
                "@" not in email or "." not in email
            ):

                st.error("Enter a valid email address.")

            elif email.strip() and any(
                s.get("email", "").lower() == email.strip().lower()
                for s in students
            ):

                st.error("This email is already registered.")

            else:

                student = {
                    "id": generate_student_id(),
                    "name": name.strip(),
                    "age": int(age),
                    "class_name": class_name.strip(),
                    "section": section.strip(),
                    "email": email.strip(),
                    "phone": phone.strip(),
                    "gender": gender,
                    "address": address.strip(),
                    "created_at": date.today().isoformat()
                }

                students.append(student)

                save_data(STUDENTS_FILE, students)

                st.success(
                    f"Student registered successfully! ID: {student['id']}"
                )

                st.rerun()


# =====================================
# 7. VIEW AND SEARCH STUDENTS
# =====================================

elif menu == "View Students":

    st.header("📋 Student Records")

    if students:

        search = st.text_input(
            "Search by ID, Name, Class, Email or Phone"
        )

        filtered_students = students

        if search.strip():

            q = search.lower().strip()

            filtered_students = [
                s for s in students
                if q in str(s["id"]).lower()
                or q in s["name"].lower()
                or q in s["class_name"].lower()
                or q in s["email"].lower()
                or q in s["phone"].lower()
            ]

        classes = sorted(set(
            s["class_name"] for s in filtered_students
        ))

        selected_class = st.selectbox(
            "Filter by Class",
            ["All"] + classes
        )

        if selected_class != "All":

            filtered_students = [
                s for s in filtered_students
                if s["class_name"] == selected_class
            ]

        st.write(
            f"Total records displayed: {len(filtered_students)}"
        )

        df = pd.DataFrame(filtered_students)

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

        st.download_button(
            "⬇️ Download Student CSV",
            df.to_csv(index=False).encode("utf-8-sig"),
            "students.csv",
            "text/csv"
        )

    else:

        st.info("No students registered yet.")


# =====================================
# 8. UPDATE STUDENT
# =====================================

elif menu == "Update Student":

    st.header("✏️ Update Student Details")

    if students:

        student_id = st.selectbox(
            "Select Student",
            [int(s["id"]) for s in students],
            format_func=lambda x: (
                f"{x} - {find_student(x)['name']}"
            )
        )

        student = find_student(student_id)

        with st.form("update_form"):

            name = st.text_input(
                "Name",
                value=student["name"]
            )

            age = st.number_input(
                "Age",
                min_value=3,
                max_value=100,
                value=int(student["age"])
            )

            class_name = st.text_input(
                "Class",
                value=student["class_name"]
            )

            section = st.text_input(
                "Section",
                value=student.get("section", "")
            )

            email = st.text_input(
                "Email",
                value=student.get("email", "")
            )

            phone = st.text_input(
                "Phone",
                value=student.get("phone", "")
            )

            address = st.text_area(
                "Address",
                value=student.get("address", "")
            )

            update = st.form_submit_button(
                "Update Student",
                type="primary"
            )

            if update:

                if not name.strip() or not class_name.strip():

                    st.error("Name and Class are required.")

                elif email.strip() and (
                    "@" not in email or "." not in email
                ):

                    st.error("Enter a valid email.")

                elif email.strip() and any(
                    int(s["id"]) != student_id
                    and s.get("email", "").lower() == email.strip().lower()
                    for s in students
                ):

                    st.error("Another student already uses this email.")

                else:

                    student.update({
                        "name": name.strip(),
                        "age": int(age),
                        "class_name": class_name.strip(),
                        "section": section.strip(),
                        "email": email.strip(),
                        "phone": phone.strip(),
                        "address": address.strip()
                    })

                    save_data(STUDENTS_FILE, students)

                    st.success("Student updated successfully!")

                    st.rerun()

    else:

        st.info("No students available.")


# =====================================
# 9. DELETE STUDENT
# =====================================

elif menu == "Delete Student":

    st.header("🗑️ Delete Student")

    if students:

        student_id = st.selectbox(
            "Select Student to Delete",
            [int(s["id"]) for s in students],
            format_func=lambda x: (
                f"{x} - {find_student(x)['name']}"
            )
        )

        student = find_student(student_id)

        st.warning(
            f"You selected: {student['name']} (ID: {student_id})"
        )

        confirm = st.checkbox(
            "I confirm that I want to delete this student."
        )

        if st.button(
            "Delete Student",
            disabled=not confirm,
            type="primary"
        ):

            students = [
                s for s in students
                if int(s["id"]) != student_id
            ]

            attendance = [
                a for a in attendance
                if int(a["student_id"]) != student_id
            ]

            marks = [
                m for m in marks
                if int(m["student_id"]) != student_id
            ]

            save_data(STUDENTS_FILE, students)
            save_data(ATTENDANCE_FILE, attendance)
            save_data(MARKS_FILE, marks)

            st.success("Student and related records deleted.")

            st.rerun()

    else:

        st.info("No student records available.")


# =====================================
# 10. ATTENDANCE MANAGEMENT
# =====================================

elif menu == "Attendance":

    st.header("📅 Attendance Management")

    if not students:

        st.info("Please register students first.")

    else:

        student_options = {
            f"{s['id']} - {s['name']}": int(s["id"])
            for s in students
        }

        with st.form("attendance_form"):

            selected = st.selectbox(
                "Select Student",
                list(student_options.keys())
            )

            attendance_date = st.date_input(
                "Attendance Date",
                value=date.today()
            )

            status = st.radio(
                "Attendance Status",
                ["Present", "Absent", "Late"],
                horizontal=True
            )

            submit = st.form_submit_button(
                "Save Attendance",
                type="primary"
            )

            if submit:

                sid = student_options[selected]

                existing = next(
                    (
                        a for a in attendance
                        if int(a["student_id"]) == sid
                        and a["date"] == attendance_date.isoformat()
                    ),
                    None
                )

                if existing:

                    existing["status"] = status

                else:

                    attendance.append({
                        "student_id": sid,
                        "date": attendance_date.isoformat(),
                        "status": status
                    })

                save_data(ATTENDANCE_FILE, attendance)

                st.success("Attendance saved successfully!")

                st.rerun()

        st.divider()

        st.subheader("Attendance History")

        if attendance:

            rows = []

            for record in attendance:

                s = find_student(record["student_id"])

                rows.append({
                    "Student ID": record["student_id"],
                    "Name": s["name"] if s else "Unknown",
                    "Date": record["date"],
                    "Status": record["status"]
                })

            df = pd.DataFrame(rows)

            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True
            )

            present_count = sum(
                1 for a in attendance
                if a["status"] == "Present"
            )

            percentage = (
                present_count / len(attendance) * 100
            )

            st.metric(
                "Overall Attendance",
                f"{percentage:.1f}%"
            )

            st.download_button(
                "Download Attendance CSV",
                df.to_csv(index=False).encode("utf-8-sig"),
                "attendance.csv",
                "text/csv"
            )

        else:

            st.info("No attendance records available.")


# =====================================
# 11. MARKS AND GRADES
# =====================================

elif menu == "Marks & Grades":

    st.header("📝 Marks and Grades Management")

    if not students:

        st.info("Please register students first.")

    else:

        student_options = {
            f"{s['id']} - {s['name']}": int(s["id"])
            for s in students
        }

        with st.form("marks_form"):

            selected = st.selectbox(
                "Select Student",
                list(student_options.keys())
            )

            subject = st.text_input("Subject Name")

            exam = st.text_input(
                "Examination Name",
                value="Unit Test"
            )

            score = st.number_input(
                "Marks Obtained",
                min_value=0.0,
                max_value=100.0,
                value=0.0
            )

            submit = st.form_submit_button(
                "Save Marks",
                type="primary"
            )

            if submit:

                if not subject.strip():

                    st.error("Enter subject name.")

                else:

                    marks.append({
                        "student_id": student_options[selected],
                        "subject": subject.strip(),
                        "exam": exam.strip(),
                        "marks": float(score),
                        "grade": grade_calculator(score),
                        "date": date.today().isoformat()
                    })

                    save_data(MARKS_FILE, marks)

                    st.success("Marks saved successfully!")

                    st.rerun()

        st.divider()

        st.subheader("Academic Records")

        if marks:

            rows = []

            for m in marks:

                s = find_student(m["student_id"])

                rows.append({
                    "Student ID": m["student_id"],
                    "Name": s["name"] if s else "Unknown",
                    "Subject": m["subject"],
                    "Exam": m["exam"],
                    "Marks": m["marks"],
                    "Grade": grade_calculator(float(m["marks"])),
                    "Date": m["date"]
                })

            df = pd.DataFrame(rows)

            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True
            )

            st.download_button(
                "Download Marks CSV",
                df.to_csv(index=False).encode("utf-8-sig"),
                "marks.csv",
                "text/csv"
            )

        else:

            st.info("No marks available.")


# =====================================
# 12. REPORTS
# =====================================

elif menu == "Reports":

    st.header("📊 Student Performance Reports")

    if students:

        report = []

        for student in students:

            sid = int(student["id"])

            student_attendance = [
                a for a in attendance
                if int(a["student_id"]) == sid
            ]

            present = sum(
                1 for a in student_attendance
                if a["status"] == "Present"
            )

            attendance_rate = (
                present / len(student_attendance) * 100
                if student_attendance else 0
            )

            student_marks = [
                float(m["marks"])
                for m in marks
                if int(m["student_id"]) == sid
            ]

            average = (
                sum(student_marks) / len(student_marks)
                if student_marks else 0
            )

            report.append({
                "ID": sid,
                "Name": student["name"],
                "Class": student["class_name"],
                "Attendance %": round(attendance_rate, 2),
                "Average Marks": round(average, 2),
                "Grade": grade_calculator(average)
                    if student_marks else "N/A"
            })

        df = pd.DataFrame(report)

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

        st.download_button(
            "⬇️ Download Performance Report",
            df.to_csv(index=False).encode("utf-8-sig"),
            "student_performance_report.csv",
            "text/csv"
        )

        fig = px.bar(
            df,
            x="Name",
            y="Average Marks",
            color="Class",
            title="Student Academic Performance"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    else:

        st.info("No student records available.")


# =====================================
# 13. BACKUP AND RESTORE
# =====================================

elif menu == "Backup & Restore":

    st.header("💾 Data Backup and Restore")

    st.write("Download your JSON database files for backup.")

    col1, col2, col3 = st.columns(3)

    col1.download_button(
        "Students Backup",
        STUDENTS_FILE.read_bytes(),
        "students.json",
        "application/json"
    )

    col2.download_button(
        "Attendance Backup",
        ATTENDANCE_FILE.read_bytes(),
        "attendance.json",
        "application/json"
    )

    col3.download_button(
        "Marks Backup",
        MARKS_FILE.read_bytes(),
        "marks.json",
        "application/json"
    )

    st.divider()

    st.subheader("Restore JSON Backup")

    st.warning(
        "Restoring a backup replaces the selected database file. "
        "Download your current data before restoring."
    )

    backup_type = st.selectbox(
        "Select Database",
        ["Students", "Attendance", "Marks"]
    )

    uploaded_file = st.file_uploader(
        "Upload JSON Backup",
        type=["json"]
    )

    if uploaded_file:

        if st.button("Restore Backup", type="primary"):

            try:

                restored_data = json.loads(
                    uploaded_file.getvalue().decode("utf-8")
                )

                if not isinstance(restored_data, list):
                    raise ValueError("JSON must contain a list.")

                target_file = {
                    "Students": STUDENTS_FILE,
                    "Attendance": ATTENDANCE_FILE,
                    "Marks": MARKS_FILE
                }[backup_type]

                save_data(target_file, restored_data)

                st.success("Backup restored successfully!")

                st.rerun()

            except (json.JSONDecodeError, UnicodeDecodeError, ValueError) as error:

                st.error(f"Restore failed: {error}")


# =====================================
# 14. FOOTER
# =====================================

st.sidebar.divider()

st.sidebar.caption(
    "Advanced Student Management System"
)

st.sidebar.caption(
    "Developed using Python, Streamlit and JSON"
)
