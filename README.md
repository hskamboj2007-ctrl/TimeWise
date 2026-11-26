# TimeWise: Intelligent Task Scheduling & Productivity Dashboard

A modern, full-stack mini-project built with **HTML**, **CSS**, **JavaScript**, **Python**, and **SQLite**. Designed to be completely responsive across both **mobile phones** and **laptops**, featuring an animated **Plant Growth Visualization** and **Weekly/Monthly Report Line Graphs**.

---

## 🌟 Key Features

| Feature | Description |
| :--- | :--- |
| **User Dashboard** | Displays overall productivity, greeting, 4 pastel stat cards (*Total Tasks*, *Completed*, *Pending*, *Progress*), and today's tasks. |
| **Add Task** | Add new tasks with title, duration (hours & minutes), priority level, deadline, and category. |
| **Set Deadline** | Option to choose whether a task has a deadline or is flexible, with clock time selection. |
| **Priority Levels** | Color-coded `High`, `Medium`, and `Low` priority tags. |
| **Smart Scheduling (Python)** | AI heuristic optimization arranging tasks by priority, deadline urgency, and daily available study/work time. |
| **Task Status** | Interactive toggle between `Pending` and `Completed` with celebratory feedback. |
| **Time Management** | Fits tasks into user's daily study/work window and defers tasks that exceed capacity. |
| **Plant Growth Tracker** | Interactive SVG plant that grows as tasks are completed (Seed $\rightarrow$ Sprout $\rightarrow$ Seedling $\rightarrow$ Vegetative $\rightarrow$ Budding $\rightarrow$ Fully Bloomed Flower $\rightarrow$ Celebrations). |
| **Productivity Analytics Graph** | Canvas-based Bezier line chart supporting both **Weekly** (Mon–Sun) and **Monthly** (Week 1–4) views with hover tooltips and metrics. |
| **Daily Planner** | Chronological timeline slots showing planned execution windows. |

---

## 🛠️ Technology Stack Breakdown

- **HTML (`index.html`)**: Clean semantic structure matching mobile and laptop layouts.
- **CSS (`style.css`)**: Responsive styling with modern pastel palette matching the screenshot.
- **JavaScript (`app.js`)**: Dynamic state management, SVG plant rendering, canvas line chart, and API client.
- **Python (`app.py`, `scheduler.py`)**: REST API server and multi-objective smart scheduling algorithm.
- **SQLite (`database.py`, `timewise.db`)**: Persistent database storing tasks, settings, and completion history.

---

## 🚀 How to Run the Project

### Running with the Python Backend (Recommended)
1. Open PowerShell or Command Prompt in this folder:
   ```bash
   python app.py
   ```
2. Open your web browser and navigate to:
   ```
   http://localhost:5000
   ```

### Running Standalone (Direct Browser Launch)
You can also directly double-click `index.html` in Chrome, Edge, or Firefox. The built-in client-side engine will run with full interactivity and local data!
