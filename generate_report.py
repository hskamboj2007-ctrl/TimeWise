"""
TimeWise - Project Explainer & Team Distribution Report Generator
Generates a comprehensive, professional PDF report saved directly to the Desktop.
"""

import os
import sys
import subprocess
from datetime import datetime

DESKTOP_DIR = os.path.join(os.environ.get("USERPROFILE", "C:\\Users\\hp"), "OneDrive", "Desktop")
if not os.path.exists(DESKTOP_DIR):
    DESKTOP_DIR = os.path.join(os.environ.get("USERPROFILE", "C:\\Users\\hp"), "Desktop")

PDF_PATH = os.path.join(DESKTOP_DIR, "TimeWise_Project_Report.pdf")
HTML_PATH = os.path.join(os.getcwd(), "report_temp.html")

html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>TimeWise - Project Explainer & Team Distribution Report</title>
    <style>
        @page {
            size: A4;
            margin: 15mm 15mm 15mm 15mm;
        }
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
        }
        body {
            background: #ffffff;
            color: #1e293b;
            line-height: 1.5;
            font-size: 13px;
        }
        .header {
            border-bottom: 3px solid #2563eb;
            padding-bottom: 14px;
            margin-bottom: 20px;
        }
        .badge {
            display: inline-block;
            background: #dcfce7;
            color: #15803d;
            font-size: 11px;
            font-weight: 700;
            padding: 3px 10px;
            border-radius: 12px;
            text-transform: uppercase;
            margin-bottom: 6px;
        }
        h1 {
            font-size: 24px;
            font-weight: 800;
            color: #0f172a;
            margin-bottom: 4px;
        }
        .subtitle {
            font-size: 13px;
            color: #64748b;
            margin-bottom: 10px;
        }
        .meta-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 10px;
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 10px 14px;
            font-size: 12px;
        }
        .meta-item strong {
            display: block;
            color: #0f172a;
            font-size: 11px;
            text-transform: uppercase;
        }
        .section-title {
            font-size: 16px;
            font-weight: 700;
            color: #0f172a;
            border-left: 4px solid #2563eb;
            padding-left: 8px;
            margin: 20px 0 10px 0;
        }
        p {
            margin-bottom: 8px;
            color: #334155;
        }
        /* Member Card Grid */
        .members-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 14px;
            margin-bottom: 16px;
        }
        .member-card {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 10px;
            padding: 14px;
            page-break-inside: avoid;
            box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        }
        .member-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 6px;
        }
        .member-name {
            font-size: 15px;
            font-weight: 700;
            color: #0f172a;
        }
        .member-role {
            font-size: 11px;
            font-weight: 700;
            padding: 2px 8px;
            border-radius: 12px;
        }
        .role-fe { background: #e0e7ff; color: #3730a3; }
        .role-be { background: #dcfce7; color: #166534; }
        .role-algo { background: #fef3c7; color: #92400e; }
        .role-ui { background: #f3e8ff; color: #6b21a8; }
        .member-desc {
            font-size: 11.5px;
            color: #64748b;
            margin-bottom: 8px;
            font-style: italic;
        }
        .task-list {
            list-style: none;
            padding-left: 0;
            font-size: 11.5px;
        }
        .task-list li {
            position: relative;
            padding-left: 14px;
            margin-bottom: 4px;
            color: #334155;
        }
        .task-list li::before {
            content: "•";
            color: #2563eb;
            position: absolute;
            left: 2px;
            font-weight: bold;
        }
        /* Tables */
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 10px 0 16px 0;
            font-size: 11.5px;
        }
        th, td {
            border: 1px solid #cbd5e1;
            padding: 6px 10px;
            text-align: left;
        }
        th {
            background: #f1f5f9;
            color: #0f172a;
            font-weight: 700;
        }
        .callout-box {
            background: #eff6ff;
            border: 1px solid #bfdbfe;
            border-radius: 8px;
            padding: 10px 14px;
            margin-bottom: 14px;
            font-size: 12px;
        }
        .callout-box strong {
            color: #1e40af;
        }
        .page-break {
            page-break-after: always;
        }
        .footer-note {
            text-align: center;
            font-size: 11px;
            color: #94a3b8;
            border-top: 1px solid #e2e8f0;
            padding-top: 8px;
            margin-top: 16px;
        }
    </style>
</head>
<body>

    <!-- PAGE 1: COVER & EXECUTIVE SUMMARY -->
    <div class="header">
        <span class="badge">Project Presentation & Viva Explainer</span>
        <h1>TimeWise: Intelligent Task Scheduling and Time Management System</h1>
        <p class="subtitle">A full-stack, AI-heuristic productivity dashboard for students and professionals.</p>
        <div class="meta-grid">
            <div class="meta-item"><strong>Date:</strong> November 2026</div>
            <div class="meta-item"><strong>Tech Stack:</strong> Python, SQLite, HTML5, CSS3, JS</div>
            <div class="meta-item"><strong>Team Size:</strong> 4 Students</div>
            <div class="meta-item"><strong>Repository:</strong> github.com/hskamboj2007-ctrl/TimeWise</div>
        </div>
    </div>

    <div class="section-title">1. Executive Summary & Problem Statement</div>
    <p>
        Traditional timetable applications are rigid and static: they do not adapt when tasks exceed their planned time, fail to optimize for tight deadlines, and offer no psychological motivation. <strong>TimeWise</strong> solves this by introducing a dynamic, intelligent task scheduling web application backed by Python multi-objective optimization algorithms, a persistent SQLite database, and an animated gamified progress tracker.
    </p>

    <div class="section-title">2. Team Roles & Individual Contributions (4 Students)</div>
    <p>The development of TimeWise was modularly divided among 4 team members, allowing each student to own an independent, critical domain of the application:</p>

    <div class="members-grid">
        <!-- STUDENT 1 -->
        <div class="member-card">
            <div class="member-header">
                <span class="member-name">Student 1 (Hardik)</span>
                <span class="member-role role-fe">Frontend Lead</span>
            </div>
            <div class="member-desc">UI/UX Architecture, Layout Responsiveness & Modal System</div>
            <ul class="task-list">
                <li>Designed responsive layout functioning seamlessly on both Mobile & Laptop screens.</li>
                <li>Created the 4 pastel stat cards (Total Tasks: 08, Completed: 05, Pending: 03, Progress: 62%).</li>
                <li>Implemented the dynamic time-of-day greeting ("Good afternoon!").</li>
                <li>Engineered the Add Task modal with input validation and native Date Picker for deadlines.</li>
                <li>Built modular CSS architecture using CSS custom properties (variables) and transitions.</li>
            </ul>
        </div>

        <!-- STUDENT 2 -->
        <div class="member-card">
            <div class="member-header">
                <span class="member-name">Student 2</span>
                <span class="member-role role-be">Backend & Database</span>
            </div>
            <div class="member-desc">REST API Architecture, SQLite Schema & State Persistence</div>
            <ul class="task-list">
                <li>Built the zero-dependency Python HTTP server (<code>app.py</code>) with CORS support.</li>
                <li>Designed the SQLite database schema (<code>database.py</code>) with tasks, settings & history.</li>
                <li>Engineered REST endpoints: <code>/api/tasks</code>, <code>/api/stats</code>, <code>/api/schedule</code>.</li>
                <li>Implemented instant task completion toggle endpoint (<code>/api/tasks/&lt;id&gt;/toggle</code>).</li>
                <li>Pre-seeded realistic test datasets ensuring smooth out-of-the-box viva demonstrations.</li>
            </ul>
        </div>

        <!-- STUDENT 3 -->
        <div class="member-card">
            <div class="member-header">
                <span class="member-name">Student 3</span>
                <span class="member-role role-algo">Algorithm Specialist</span>
            </div>
            <div class="member-desc">Smart Scheduling Heuristic, Time Management & Deferrals</div>
            <ul class="task-list">
                <li>Designed the Python Smart Scheduling algorithm (<code>scheduler.py</code>) using multi-objective scoring.</li>
                <li>Integrated Priority weighting (High=3, Medium=2, Low=1) with Deadline Date urgency.</li>
                <li>Engineered the bounded time allocation engine producing concrete start & end timeline slots.</li>
                <li>Implemented the Dynamic Task Deferral System when total task time exceeds the daily work window.</li>
                <li>Added the interactive Work Limit selector (4h, 6h, 8h, 10h, 12h) with dynamic rescheduling.</li>
            </ul>
        </div>

        <!-- STUDENT 4 -->
        <div class="member-card">
            <div class="member-header">
                <span class="member-name">Student 4</span>
                <span class="member-role role-ui">Gamification & Analytics</span>
            </div>
            <div class="member-desc">SVG Plant Growth Engine, Canvas Line Chart & Version Control</div>
            <ul class="task-list">
                <li>Designed and coded the 6-stage procedural SVG Plant Growth Tracker (Seed to Full Bloom).</li>
                <li>Tied live plant growth animation directly to task completion percentages.</li>
                <li>Engineered the interactive HTML5 Canvas Line Chart supporting Weekly & Monthly views.</li>
                <li>Implemented smooth Bezier curve rendering, gradient area fill, and interactive hover tooltips.</li>
                <li>Managed Git version control, GitHub repository synchronization, and project documentation.</li>
            </ul>
        </div>
    </div>

    <div class="page-break"></div>

    <!-- PAGE 2: ARCHITECTURE & EVALUATION CHECKLIST -->
    <div class="section-title">3. System Architecture & Technology Stack</div>
    <table>
        <thead>
            <tr>
                <th>Technology</th>
                <th>Component / Module</th>
                <th>Key Responsibility & Function</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td><strong>HTML5</strong></td>
                <td><code>index.html</code></td>
                <td>Semantic layout for mobile cards, grid dashboard, interactive modal & SVG plant container.</td>
            </tr>
            <tr>
                <td><strong>CSS3</strong></td>
                <td><code>style.css</code></td>
                <td>Custom pastel color palette, responsive media queries, card hover transitions & toast popups.</td>
            </tr>
            <tr>
                <td><strong>JavaScript</strong></td>
                <td><code>app.js</code></td>
                <td>State synchronization, dynamic DOM updates, canvas line chart rendering & client fallback engine.</td>
            </tr>
            <tr>
                <td><strong>Python</strong></td>
                <td><code>app.py</code> & <code>scheduler.py</code></td>
                <td>Micro-framework REST backend and heuristic time-knapsack scheduling optimization logic.</td>
            </tr>
            <tr>
                <td><strong>SQLite</strong></td>
                <td><code>database.py</code> & <code>timewise.db</code></td>
                <td>Relational persistent storage for tasks, deadline dates, user preferences & weekly history.</td>
            </tr>
        </tbody>
    </table>

    <div class="section-title">4. Deep Dive into Key Project Innovations</div>

    <div class="callout-box">
        <strong>Feature A: Gamified Plant Growth Tracker</strong><br>
        Traditional to-do lists trigger no emotional reward. TimeWise implements a psychology-backed gamification loop: completing tasks waters and nourishes a virtual plant through 6 visual stages:
        <ul style="margin: 4px 0 0 16px;">
            <li><strong>0%:</strong> Seed resting in soil with floating watering drop.</li>
            <li><strong>1-24%:</strong> Green sprout breaking through soil (Sprout).</li>
            <li><strong>25-49%:</strong> Seedling with 4 expanding vibrant leaves.</li>
            <li><strong>50-74%:</strong> Bushy, multi-branched vegetative plant.</li>
            <li><strong>75-99%:</strong> Mature plant with budding flower heads.</li>
            <li><strong>100%:</strong> Fully blossomed glorious flower with golden sparkles and celebration toast!</li>
        </ul>
    </div>

    <div class="callout-box">
        <strong>Feature B: Smart Scheduling & Daily Time Window Control</strong><br>
        The Python scheduling engine uses a multi-objective scoring formula:
        $$\text{Score} = (\text{Priority Weight} \times 50) + \text{Deadline Urgency Bonus} + \text{Duration Density}$$
        Tasks due today or tomorrow receive top urgency. If tasks exceed the student's daily work window (e.g. 6 hours), lower-priority tasks (e.g., Project Work - 2h) are automatically moved to the <em>"Deferred to Tomorrow"</em> box. If the student expands their window to 8 hours, TimeWise instantly schedules it into today's timeline!
    </div>

    <div class="callout-box">
        <strong>Feature C: Weekly & Monthly Productivity Line Chart</strong><br>
        An interactive HTML5 Canvas element computes weekly (Mon–Sun) and monthly (Week 1–4) trends using smooth Bezier interpolation. Hovering over any data point reveals the completion percentage and exact task ratio.
    </div>

    <div class="section-title">5. Teacher Viva / Evaluation Q&A Guide</div>
    <table>
        <thead>
            <tr>
                <th style="width: 35%;">Likely Question from Teacher</th>
                <th style="width: 65%;">Recommended Technical Answer</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td><strong>"Why did you use Python for scheduling?"</strong></td>
                <td>Python provides native support for algorithmic optimization, clean mathematical modeling, and easy extensibility to machine learning models without heavy server overhead.</td>
            </tr>
            <tr>
                <td><strong>"What happens when a task exceeds available time?"</strong></td>
                <td>The system prioritizes high-impact and urgent deadline tasks. Over-capacity tasks are safely deferred to the next day's queue to prevent student burnout.</td>
            </tr>
            <tr>
                <td><strong>"Is the data saved permanently?"</strong></td>
                <td>Yes. All tasks, deadlines, completion timestamps, and work hours are persistently stored in the SQLite database (<code>timewise.db</code>).</td>
            </tr>
            <tr>
                <td><strong>"Does the app work without internet?"</strong></td>
                <td>Yes. It runs completely offline on <code>localhost:5000</code> with zero third-party cloud or external pip dependencies.</td>
            </tr>
        </tbody>
    </table>

    <div class="footer-note">
        TimeWise Project Report &bull; Generated for Evaluation Committee &bull; Saved to Desktop
    </div>

</body>
</html>
"""

# Write HTML file
with open(HTML_PATH, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"Temporary HTML report generated at: {HTML_PATH}")

# Convert to PDF using Microsoft Edge headless
edge_paths = [
    "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
    "C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe"
]

edge_exe = None
for p in edge_paths:
    if os.path.exists(p):
        edge_exe = p
        break

pdf_generated = False
if edge_exe:
    cmd = [
        edge_exe,
        "--headless",
        "--disable-gpu",
        "--no-pdf-header-footer",
        f"--print-to-pdf={PDF_PATH}",
        HTML_PATH
    ]
    print(f"Running Microsoft Edge to generate PDF at: {PDF_PATH}")
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        if os.path.exists(PDF_PATH) and os.path.getsize(PDF_PATH) > 1000:
            print(f"SUCCESS: PDF successfully generated via Edge ({os.path.getsize(PDF_PATH)} bytes).")
            pdf_generated = True
    except Exception as e:
        print(f"Edge headless error: {e}")

# Fallback using ReportLab if Edge was not available
if not pdf_generated:
    print("Edge conversion skipped or failed. Falling back to ReportLab...")
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors

    doc = SimpleDocTemplate(PDF_PATH, pagesize=A4, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=20, leading=24, textColor=colors.HexColor('#0f172a'))
    h2_style = ParagraphStyle('H2Style', parent=styles['Heading2'], fontSize=14, leading=18, textColor=colors.HexColor('#2563eb'), spaceBefore=12, spaceAfter=6)
    body_style = ParagraphStyle('BodyStyle', parent=styles['Normal'], fontSize=10, leading=14, textColor=colors.HexColor('#334155'))

    story = []
    story.append(Paragraph("TimeWise: Intelligent Task Scheduling System", title_style))
    story.append(Paragraph("Project Explainer & Team Distribution Report", h2_style))
    story.append(Spacer(1, 12))

    story.append(Paragraph("1. Executive Summary", h2_style))
    story.append(Paragraph("TimeWise is a full-stack smart scheduling and time management web application developed in Python, SQLite, HTML5, CSS3, and JavaScript. It features multi-objective heuristic scheduling, dynamic task deferral, an animated plant growth tracker, and weekly/monthly performance line charts.", body_style))
    story.append(Spacer(1, 12))

    story.append(Paragraph("2. Team Roles & Task Distribution (4 Students)", h2_style))
    
    table_data = [
        ["Member", "Assigned Role", "Key Contributions & Completed Tasks"],
        ["Student 1 (Hardik)", "Frontend Lead", "Designed mobile & laptop responsive UI, 4 pastel cards, greeting & Add Task modal."],
        ["Student 2", "Backend & Database", "Built Python HTTP server, SQLite schema, REST endpoints, and persistence."],
        ["Student 3", "Algorithm Specialist", "Designed Python smart scheduling heuristic, priority weights & task deferrals."],
        ["Student 4", "Gamification & Analytics", "Created 6-stage SVG Plant Growth tracker, Canvas line chart & Git repo."]
    ]
    t = Table(table_data, colWidths=[90, 110, 320])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f1f5f9')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor('#0f172a')),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
    ]))
    story.append(t)
    doc.build(story)
    print(f"SUCCESS: ReportLab PDF generated at: {PDF_PATH}")

# Clean up temp HTML
if os.path.exists(HTML_PATH):
    try:
        os.remove(HTML_PATH)
    except Exception:
        pass

print(f"PDF Output Location: {PDF_PATH}")
