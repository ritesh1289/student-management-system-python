
import streamlit as st
import pandas as pd
import plotly.express as px
import json
import re
import io
from pathlib import Path
from datetime import date

# ==========================================
# PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="Advanced Student Management System",
    page_icon="🎓",
    layout="wide"
)

# ==========================================
# FILE CONFIGURATION
# ==========================================

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

STUDENT_FILE = DATA_DIR / "students.json"
ATTENDANCE_FILE = DATA_DIR / "attendance.json"


def initialize_file(file_path):
    if not file_path.exists():
        file_path.write_text("[]", encoding="utf-8")


initialize_file(STUDENT_FILE)
initialize_file(ATTENDANCE_FILE)


def load_json(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
            return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def save_json(file_path, data):
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


# ==========================================
# DATA FUNCTIONS
# ==========================================

def load_students():
    return load_json(STUDENT_FILE)


def load_attendance():
    return load_json(ATTENDANCE_FILE)


def save_students(students):
    save_json(STUDENT_FILE, students)


def save_attendance(records):
    save_json(ATTENDANCE_FILE, records)


def calculate_grade(percentage):
    if percentage >= 90:
        return "A+"
    elif percentage >= 80:
        return "A"
    elif percentage >= 70:
        return "B"
    elif percentage >= 60:
        return "C"
    elif percentage >= 50:
        return "D"
    elif percentage >= 40:
        return "E"
    return "F"


def calculate_percentage(subjects):
    if not subjects:
        return 0.0

    marks = list(subjects.values())

    if not marks:
        return 0.0

    return round(sum(marks) / len(marks), 2)


def student_exists(students, student_id, email, exclude_id=None):
    for student in students:
        if student["id"] == student_id and student["id"] != exclude_id:
            return "Student ID already exists."

        if student["email"].lower() == email.lower():
            if student["id"] != exclude_id:
                return "Email already exists."

    return None


def get_student(student_id):
    for student in load_students():
        if student["id"] == student_id:
            return student
    return None


def make_student_dataframe(students, attendance):
    rows = []

    for student in students:
        subjects = student.get("subjects", {})
        percentage = calculate_percentage(subjects)

        student_records = [
            record for record in attendance
            if record.get("student_id") == student["id"]
        ]

        total_days = len(student_records)
        present_days = sum(
            1 for record in student_records
            if record.get("status") == "Present"
        )

        attendance_percentage = (
            round(present_days / total_days * 100, 2)
            if total_days else 0
        )

        rows.append({
            "ID": student["id"],
            "Name": student["name"],
            "Email": student["email"],
            "Class": student["class"],
            "Age": student["age"],
            "Subjects": len(subjects),
            "Total Marks": sum(subjects.values()),
            "Percentage": percentage,
            "Grade": calculate_grade(percentage),
            "Attendance": attendance_percentage
        })

    return pd.DataFrame(rows)


# ==========================================
# LOAD DATA
# ==========================================

students = load_students()
attendance = load_attendance()

# ==========================================
# HEADER
# ==========================================

st.title("🎓 Advanced Student Management System")
st.caption("Manage student profiles, academic records, attendance and reports.")

# ==========================================
# SIDEBAR NAVIGATION
# ==========================================

st.sidebar.title("Navigation")

page = st.sidebar.radio(
    "Select Module",
    [
        "Dashboard",
        "Add Student",
        "View Students",
        "Edit Student",
        "Delete Student",
        "Academic Records",
        "Attendance",
        "Reports"
    ]
)

# ==========================================
# DASHBOARD
# ==========================================

if page == "Dashboard":

    st.header("📊 Dashboard Overview")

    df = make_student_dataframe(students, attendance)

    total_students = len(students)

    average_percentage = (
        df["Percentage"].mean() if not df.empty else 0
    )

    total_classes = (
        df["Class"].nunique() if not df.empty else 0
    )

    total_present = sum(
        1 for record in attendance
        if record.get("status") == "Present"
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Total Students", total_students)
    c2.metric("Average Percentage", f"{average_percentage:.2f}%")
    c3.metric("Total Classes", total_classes)
    c4.metric("Present Records", total_present)

    st.divider()

    if not df.empty:

        left, right = st.columns(2)

        with left:
            st.subheader("Students by Class")

            class_data = (
                df.groupby("Class")
                .size()
                .reset_index(name="Students")
            )

            fig = px.pie(
                class_data,
                names="Class",
                values="Students",
                hole=0.4,
                title="Class Distribution"
            )

            st.plotly_chart(fig, use_container_width=True)

        with right:
            st.subheader("Student Performance")

            fig = px.bar(
                df,
                x="Name",
                y="Percentage",
                color="Grade",
                title="Student Percentage",
                hover_data=["Class", "Grade"]
            )

            st.plotly_chart(fig, use_container_width=True)

        st.subheader("Recent Student Records")
        st.dataframe(df.tail(10), use_container_width=True)

    else:
        st.info("No student records available. Add your first student.")

# ==========================================
# ADD STUDENT
# ==========================================

elif page == "Add Student":

    st.header("➕ Add New Student")

    with st.form("add_student_form"):

        col1, col2 = st.columns(2)

        with col1:
            student_id = st.text_input("Student ID")
            name = st.text_input("Full Name")
            email = st.text_input("Email Address")

        with col2:
            student_class = st.text_input("Class / Department")
            age = st.number_input(
                "Age",
                min_value=3,
                max_value=100,
                value=18
            )

        st.subheader("Academic Marks")

        m1, m2, m3 = st.columns(3)

        with m1:
            maths = st.number_input(
                "Maths",
                min_value=0,
                max_value=100,
                value=0
            )

        with m2:
            python = st.number_input(
                "Python",
                min_value=0,
                max_value=100,
                value=0
            )

        with m3:
            english = st.number_input(
                "English",
                min_value=0,
                max_value=100,
                value=0
            )

        submitted = st.form_submit_button(
            "Save Student",
            use_container_width=True
        )

        if submitted:

            student_id = student_id.strip()
            name = name.strip()
            email = email.strip()
            student_class = student_class.strip()

            if not all([student_id, name, email, student_class]):
                st.error("Please fill in all required fields.")

            elif not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
                st.error("Enter a valid email address.")

            else:

                error = student_exists(
                    students,
                    student_id,
                    email
                )

                if error:
                    st.error(error)

                else:

                    new_student = {
                        "id": student_id,
                        "name": name,
                        "email": email,
                        "class": student_class,
                        "age": int(age),
                        "subjects": {
                            "Maths": int(maths),
                            "Python": int(python),
                            "English": int(english)
                        }
                    }

                    students.append(new_student)
                    save_students(students)

                    st.success(
                        f"Student {name} added successfully!"
                    )
                    st.rerun()

# ==========================================
# VIEW STUDENTS + SMART SEARCH
# ==========================================

elif page == "View Students":

    st.header("👨‍🎓 Student Records")

    df = make_student_dataframe(students, attendance)

    if df.empty:
        st.info("No students found.")

    else:

        search = st.text_input(
            "🔍 Search by ID, Name, Class or Email"
        )

        classes = sorted(df["Class"].unique().tolist())

        selected_classes = st.multiselect(
            "Filter by Class",
            classes,
            default=classes
        )

        grades = sorted(df["Grade"].unique().tolist())

        selected_grades = st.multiselect(
            "Filter by Grade",
            grades,
            default=grades
        )

        age_range = st.slider(
            "Filter by Age",
            min_value=3,
            max_value=100,
            value=(3, 100)
        )

        filtered = df[
            (df["Class"].isin(selected_classes)) &
            (df["Grade"].isin(selected_grades)) &
            (df["Age"].between(age_range[0], age_range[1]))
        ].copy()

        if search.strip():

            search = search.strip().lower()

            mask = (
                filtered["ID"].astype(str).str.lower().str.contains(
                    search, regex=False
                ) |
                filtered["Name"].astype(str).str.lower().str.contains(
                    search, regex=False
                ) |
                filtered["Class"].astype(str).str.lower().str.contains(
                    search, regex=False
                ) |
                filtered["Email"].astype(str).str.lower().str.contains(
                    search, regex=False
                )
            )

            filtered = filtered[mask]

        sort_column = st.selectbox(
            "Sort By",
            ["Name", "ID", "Age", "Percentage", "Attendance"]
        )

        ascending = st.checkbox("Ascending order", value=True)

        filtered = filtered.sort_values(
            by=sort_column,
            ascending=ascending
        )

        st.write(f"Found {len(filtered)} student(s).")

        st.dataframe(
            filtered,
            use_container_width=True,
            hide_index=True
        )

# ==========================================
# EDIT STUDENT
# ==========================================

elif page == "Edit Student":

    st.header("✏️ Edit Student Details")

    if not students:
        st.info("No students available.")
    else:

        student_ids = [s["id"] for s in students]

        selected_id = st.selectbox(
            "Select Student ID",
            student_ids
        )

        student = get_student(selected_id)

        if student:

            subjects = student.get("subjects", {})

            with st.form("edit_student_form"):

                name = st.text_input(
                    "Name",
                    value=student["name"]
                )

                email = st.text_input(
                    "Email",
                    value=student["email"]
                )

                student_class = st.text_input(
                    "Class",
                    value=student["class"]
                )

                age = st.number_input(
                    "Age",
                    min_value=3,
                    max_value=100,
                    value=int(student["age"])
                )

                st.subheader("Update Marks")

                maths = st.number_input(
                    "Maths",
                    min_value=0,
                    max_value=100,
                    value=int(subjects.get("Maths", 0))
                )

                python = st.number_input(
                    "Python",
                    min_value=0,
                    max_value=100,
                    value=int(subjects.get("Python", 0))
                )

                english = st.number_input(
                    "English",
                    min_value=0,
                    max_value=100,
                    value=int(subjects.get("English", 0))
                )

                update = st.form_submit_button(
                    "Update Student",
                    use_container_width=True
                )

                if update:

                    name = name.strip()
                    email = email.strip()
                    student_class = student_class.strip()

                    if not all([name, email, student_class]):
                        st.error("All fields are required.")

                    elif not re.fullmatch(
                        r"[^@\s]+@[^@\s]+\.[^@\s]+",
                        email
                    ):
                        st.error("Enter a valid email address.")

                    else:

                        error = student_exists(
                            students,
                            selected_id,
                            email,
                            exclude_id=selected_id
                        )

                        if error:
                            st.error(error)

                        else:

                            student["name"] = name
                            student["email"] = email
                            student["class"] = student_class
                            student["age"] = int(age)

                            student["subjects"] = {
                                "Maths": int(maths),
                                "Python": int(python),
                                "English": int(english)
                            }

                            save_students(students)

                            st.success("Student updated successfully!")
                            st.rerun()

# ==========================================
# DELETE STUDENT
# ==========================================

elif page == "Delete Student":

    st.header("🗑️ Delete Student")

    if not students:
        st.info("No student records available.")

    else:

        student_ids = [s["id"] for s in students]

        selected_id = st.selectbox(
            "Select Student ID to Delete",
            student_ids
        )

        student = get_student(selected_id)

        if student:

            st.warning(
                f"You are about to delete {student['name']} "
                f"({student['id']})."
            )

            confirm = st.checkbox(
                "I confirm that I want to delete this student."
            )

            if st.button(
                "Delete Student",
                type="primary",
                disabled=not confirm
            ):

                students = [
                    s for s in students
                    if s["id"] != selected_id
                ]

                attendance = [
                    r for r in attendance
                    if r.get("student_id") != selected_id
                ]

                save_students(students)
                save_attendance(attendance)

                st.success("Student and related attendance deleted.")
                st.rerun()

# ==========================================
# ACADEMIC RECORDS
# ==========================================

elif page == "Academic Records":

    st.header("📚 Academic Records")

    if not students:
        st.info("Add students first.")

    else:

        student_ids = [s["id"] for s in students]

        selected_id = st.selectbox(
            "Select Student",
            student_ids
        )

        student = get_student(selected_id)

        if student:

            subjects = student.get("subjects", {})

            percentage = calculate_percentage(subjects)
            grade = calculate_grade(percentage)
            total = sum(subjects.values())

            c1, c2, c3 = st.columns(3)

            c1.metric("Total Marks", total)
            c2.metric("Percentage", f"{percentage}%")
            c3.metric("Grade", grade)

            if subjects:

                marks_df = pd.DataFrame(
                    list(subjects.items()),
                    columns=["Subject", "Marks"]
                )

                st.subheader(
                    f"Marks of {student['name']}"
                )

                fig = px.bar(
                    marks_df,
                    x="Subject",
                    y="Marks",
                    color="Subject",
                    title="Subject-wise Performance",
                    range_y=[0, 100]
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )

                st.dataframe(
                    marks_df,
                    use_container_width=True,
                    hide_index=True
                )

            else:
                st.info("No academic records available.")

            if percentage >= 40:
                st.success("Result: PASS")
            else:
                st.error("Result: FAIL")

# ==========================================
# ATTENDANCE MANAGEMENT
# ==========================================

elif page == "Attendance":

    st.header("📅 Attendance Management")

    if not students:
        st.info("Add students before marking attendance.")

    else:

        tab1, tab2 = st.tabs([
            "Mark Attendance",
            "Attendance Report"
        ])

        with tab1:

            student_ids = [s["id"] for s in students]

            with st.form("attendance_form"):

                selected_id = st.selectbox(
                    "Select Student ID",
                    student_ids
                )

                attendance_date = st.date_input(
                    "Attendance Date",
                    value=date.today()
                )

                status = st.radio(
                    "Attendance Status",
                    ["Present", "Absent"],
                    horizontal=True
                )

                save_attendance_button = st.form_submit_button(
                    "Save Attendance"
                )

                if save_attendance_button:

                    duplicate = any(
                        r.get("student_id") == selected_id
                        and r.get("date") == str(attendance_date)
                        for r in attendance
                    )

                    if duplicate:
                        st.error(
                            "Attendance is already marked "
                            "for this student on this date."
                        )

                    else:

                        attendance.append({
                            "student_id": selected_id,
                            "date": str(attendance_date),
                            "status": status
                        })

                        save_attendance(attendance)

                        st.success("Attendance saved successfully!")
                        st.rerun()

        with tab2:

            if attendance:

                attendance_df = pd.DataFrame(attendance)

                attendance_df = attendance_df.merge(
                    pd.DataFrame([
                        {
                            "student_id": s["id"],
                            "name": s["name"],
                            "class": s["class"]
                        }
                        for s in students
                    ]),
                    on="student_id",
                    how="left"
                )

                attendance_df = attendance_df.rename(
                    columns={
                        "student_id": "Student ID",
                        "name": "Student Name",
                        "class": "Class",
                        "date": "Date",
                        "status": "Status"
                    }
                )

                st.dataframe(
                    attendance_df,
                    use_container_width=True,
                    hide_index=True
                )

                st.subheader("Student Attendance Percentage")

                summary = []

                for student in students:

                    records = [
                        r for r in attendance
                        if r.get("student_id") == student["id"]
                    ]

                    total = len(records)

                    present = sum(
                        1 for r in records
                        if r.get("status") == "Present"
                    )

                    percentage = (
                        round(present / total * 100, 2)
                        if total else 0
                    )

                    summary.append({
                        "Student ID": student["id"],
                        "Name": student["name"],
                        "Total Days": total,
                        "Present": present,
                        "Absent": total - present,
                        "Attendance %": percentage
                    })

                summary_df = pd.DataFrame(summary)

                st.dataframe(
                    summary_df,
                    use_container_width=True,
                    hide_index=True
                )

            else:
                st.info("No attendance records available.")

# ==========================================
# REPORTS AND EXPORT
# ==========================================

elif page == "Reports":

    st.header("📑 Reports and Export")

    df = make_student_dataframe(students, attendance)

    if df.empty:
        st.info("No student records available for reports.")

    else:

        st.subheader("Complete Student Report")

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

        # CSV EXPORT

        csv_data = df.to_csv(index=False).encode("utf-8")

        st.download_button(
            "⬇️ Download CSV Report",
            data=csv_data,
            file_name="student_report.csv",
            mime="text/csv"
        )

        # EXCEL EXPORT

        excel_buffer = io.BytesIO()

        with pd.ExcelWriter(
            excel_buffer,
            engine="openpyxl"
        ) as writer:

            df.to_excel(
                writer,
                index=False,
                sheet_name="Students"
            )

            attendance_df = pd.DataFrame(attendance)

            attendance_df.to_excel(
                writer,
                index=False,
                sheet_name="Attendance"
            )

        st.download_button(
            "⬇️ Download Excel Report",
            data=excel_buffer.getvalue(),
            file_name="student_report.xlsx",
            mime=(
                "application/vnd.openxmlformats-officedocument."
                "spreadsheetml.sheet"
            )
        )

        st.divider()

        st.subheader("Performance Analysis")

        fig = px.histogram(
            df,
            x="Percentage",
            color="Grade",
            title="Student Percentage Distribution",
            nbins=10
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

# ==========================================
# FOOTER
# ==========================================

st.sidebar.divider()

st.sidebar.caption(
    "Advanced Student Management System"
)

st.sidebar.caption(
    "Python | Streamlit | Pandas | Plotly | JSON"
)
