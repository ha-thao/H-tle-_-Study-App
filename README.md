# Hútle - Study App

A personalized desktop study assistant designed to help UEH students centralize academic information, manage their study activities, track GPA, and make better academic decisions.

## Project Overview

**Hútle - Study App** is a Python-based desktop application developed to address the fragmented way students manage their academic information.

The application brings study-related data and utilities into a single platform, providing students with tools for course and learning-material management, GPA tracking, goal management, Lab booking, document reading, and personalized AI-assisted academic guidance.

The system was designed for students at UEH, with a focus on reducing the time spent switching between different tools and helping students better understand and manage their academic progress.

## Objectives

The application was developed to:

- Centralize students' academic data in a single platform.
- Automate GPA calculation and provide strategic GPA planning.
- Support reading and note-taking within the same application.
- Provide personalized academic guidance through an AI Advisor.
- Manage Lab room bookings with real-time validation.
- Help students track personal academic goals and progress.

## Key Features

### 1. Study & Learning Materials

The Study module allows students to manage course-related learning materials and notes.

Key functions include:

- Managing subjects and learning materials.
- Adding and editing notes associated with subjects.
- Uploading `.txt` and `.docx` files and automatically converting their contents into notes.
- Reading PDF and Word documents directly within the application.
- Using Split View to read learning materials and take notes simultaneously.

### 2. GPA Tracking & Analytics

The GPA module helps students manage their academic performance.

Features include:

- Recording detailed course scores.
- Calculating course averages and cumulative GPA.
- Tracking GPA by semester.
- Setting overall and semester GPA targets.
- Viewing the standard curriculum for the student's major.
- Visualizing academic performance using Matplotlib.

The GPA dashboard provides:

- Cumulative GPA
- Accumulated credits
- Target GPA
- Academic classification
- Grade distribution chart
- GPA progress across semesters

### 3. GPA Lifesaver

The **GPA Lifesaver** is a strategic GPA planning algorithm designed to answer:

> "What GPA do I need in my remaining courses to graduate with my target GPA?"

The system calculates the required GPA for remaining credits and generates a strategic prediction table showing how many credits can fall within different grade levels while maintaining the target GPA.

The calculation is constrained to the valid GPA range of 0.0–4.0.

### 4. Personalized AI Advisor

The application integrates an **AI Advisor** to provide personalized academic guidance.

The AI module connects to the **Groq API using the Llama 3 model** and uses a system prompt to define the AI as a UEH-focused academic assistant.

The Advisor personalizes responses using student context such as:

- Major
- Academic year
- Academic progress

Students can also quickly select their academic year to update the context used by the AI.

To prevent the user interface from freezing while waiting for the AI response, API requests are handled using Python `threading`, with the result safely returned to the main Tkinter interface.

### 5. Goal Checklist

The Checklist module allows students to set and track personal goals across four categories:

- Academic
- Certifications
- Competitions
- Other

Students can:

- Add goals
- Edit goals
- Delete goals
- Record expected and actual outcomes
- Mark goals as completed
- Track completion progress using progress bars

Goal completion status is automatically synchronized with the database.

### 6. Lab Booking

The Lab Booking module allows students to manage laboratory room reservations.

The system provides:

- Date and time selection
- Room availability checking
- Booking confirmation
- Booking history
- Member list management
- Real-time validation of the number of participants
- Custom calendar interface
- Soft-delete handling for cancelled bookings

The custom calendar also prevents users from selecting dates in the past.

### 7. Dynamic Theming

The application provides a personalized interface based on the student's major.

After login, the system retrieves the student's major from the database and automatically applies the corresponding theme to the interface.

The application also includes a Welcome Animation consisting of:

- Icon zoom-in
- Typewriter effect
- Progress bar animation

### 8. Document Reader & Split View

The application supports reading learning materials directly within the interface.

Supported formats include:

- PDF
- DOCX

PDF files are rendered using **PyMuPDF**, while Word documents are processed using **python-docx**.

The Split View interface allows students to:

- Read documents on the left.
- Take notes on the right.
- Resize the two panels.
- Maintain the user's preferred split position.

## Technical Architecture

The application follows a modular architecture centered around a main application router.

The main application acts as a central controller that switches between different functional modules without opening separate application windows.

Major modules use a `view_state` mechanism to manage their internal screens.

Examples include:

- Study: `HOME → SUBJECT → VIEWER → NOTE_EDITOR → SPLIT`
- GPA: Dashboard → Semester Results → Semester Transcript → GPA Lifesaver
- Lab Booking: Step 1 → Step 2 → Confirmation → History

## Database

The application uses **Microsoft SQL Server** with `pyodbc`.

The database contains **12 interconnected tables** organized into four main groups:

### Academic Structure

- `NGANHHOC`
- `MONHOC`
- `CHUONGTRINH_DAOTAO`

### Student Data

- `SINHVIEN`
- `SINHVIEN_MON`
- `BANGDIEM`

### Learning Materials & Targets

- `TAILIEU`
- `GHICHU`
- `MUCTIEUDIEM`
- `MUCTIEU_HOCKY`

### Utilities

- `CHECKLIST`
- `DATPHONGLAB`

The project also applies several database-related techniques, including:

- **START_MARKER** to prevent duplicate initialization of semester course data.
- **Soft Delete** for Lab booking records.
- **Pipe Encoding** for storing expected and actual checklist results.
- **Singleton Pattern** for sharing a database connection across application modules.
- Updating existing student records during registration instead of creating duplicate accounts.

## Technologies

| Technology / Library | Purpose |
|---|---|
| **Python 3** | Application logic and backend |
| **CustomTkinter** | Modern desktop GUI |
| **SQL Server** | Database management |
| **pyodbc** | Python–SQL Server connection |
| **Groq API** | AI integration |
| **Llama 3** | Personalized AI Advisor |
| **threading** | Asynchronous AI requests |
| **PyMuPDF (fitz)** | PDF rendering |
| **python-docx** | Word document processing |
| **Matplotlib** | GPA data visualization |
| **Tkinter / CustomTkinter** | GUI components and interactions |
