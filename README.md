Advanced Student Management System
Overview
A Python and Streamlit web application for managing student profiles, marks, attendance, and reports.
Features
- Dashboard metrics and interactive charts for classes and academic performance.
- Add, view, edit, and delete student records.
- Search by ID, name, class, or email.
- Filter by class, grade, and age; sort student records.
- Record Maths, Python, and English marks.
- Calculate total marks, percentage, grade, and pass/fail result.
- Mark attendance as Present or Absent by date.
- Prevent duplicate records and calculate attendance history and percentages.
- View attendance history and attendance percentages.
Technologies
- Python – programming language
- Streamlit – web application interface
- Pandas – data processing
- Plotly Express – interactive charts
- JSON – local data storage
- OpenPyXL – Excel report generation
Student-Management-System/
├── Student-Management-system.py
├── requirements.txt
├── README.md
└── data/
    ├── students.json
    └── attendance.json
Installation and Execution
1. Install Python and open the project folder in VS Code.
2. Create an environment: py -m venv .venv.
3. Activate it: .venv\Scripts\activate.
4. Install packages: python -m pip install -r requirements.txt.
5. Run: python -m streamlit run Student-Management-system.py.
6. Open http://localhost:8501 in your browser.
Requirements and Note
The app creates JSON data files automatically; use persistent storage for production.
The app creates its data folder and JSON files automatically; keep them with the project.
This project is for educational use. Use a persistent database for production deployment.
