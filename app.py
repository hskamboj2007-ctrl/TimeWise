"""
TimeWise - Python Backend Server
Runs an HTTP server with REST APIs for Tasks, SQLite Database, and Smart Scheduling.
Zero external dependencies (uses standard library http.server, sqlite3, json).
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import urllib.parse
import os
import sys

import database
import scheduler

PORT = 5000

class TimeWiseHandler(BaseHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def send_json(self, data, status_code=200):
        body = json.dumps(data).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def send_file(self, filename, content_type):
        if not os.path.exists(filename):
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"404 Not Found")
            return
        with open(filename, "rb") as f:
            content = f.read()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def read_json_body(self):
        content_len = int(self.headers.get("Content-Length", 0))
        if content_len == 0:
            return {}
        raw = self.rfile.read(content_len)
        try:
            return json.loads(raw.decode("utf-8"))
        except Exception:
            return {}

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path == "/" or path == "/index.html":
            self.send_file("index.html", "text/html; charset=utf-8")
        elif path == "/style.css":
            self.send_file("style.css", "text/css; charset=utf-8")
        elif path == "/app.js":
            self.send_file("app.js", "application/javascript; charset=utf-8")
        
        elif path == "/api/tasks":
            tasks = database.get_all_tasks()
            self.send_json({"tasks": tasks})

        elif path == "/api/stats":
            stats = database.get_stats()
            self.send_json(stats)

        elif path == "/api/settings":
            settings = database.get_settings()
            self.send_json(settings)

        elif path == "/api/history":
            hist = database.get_history_data()
            self.send_json(hist)

        elif path == "/api/schedule":
            tasks = database.get_all_tasks()
            settings = database.get_settings()
            sched = scheduler.smart_schedule(tasks, settings["available_minutes"], settings["day_start_time"])
            self.send_json(sched)

        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        body = self.read_json_body()

        if path == "/api/tasks":
            title = body.get("title", "New Task")
            duration = int(body.get("duration", 30))
            priority = body.get("priority", "Medium")
            has_deadline = bool(body.get("has_deadline", True))
            deadline_date = body.get("deadline_date", "")
            category = body.get("category", "General")

            new_id = database.add_task(
                title=title,
                duration=duration,
                priority=priority,
                has_deadline=has_deadline,
                deadline_date=deadline_date,
                category=category
            )
            self.send_json({"status": "created", "id": new_id}, 201)

        elif path == "/api/settings":
            day_start = body.get("day_start_time", "09:00")
            avail = int(body.get("available_minutes", 240))
            database.update_settings(day_start, avail)
            self.send_json({"status": "updated"})

        elif path == "/api/smart-schedule":
            tasks = database.get_all_tasks()
            settings = database.get_settings()
            avail = int(body.get("available_minutes", settings["available_minutes"]))
            day_start = body.get("day_start_time", settings["day_start_time"])

            sched = scheduler.smart_schedule(tasks, avail, day_start)

            for item in sched["scheduled_tasks"]:
                database.update_task_schedule(item["id"], item["scheduled_start"], item["scheduled_end"])

            self.send_json(sched)

        elif path.startswith("/api/tasks/") and path.endswith("/toggle"):
            parts = path.strip("/").split("/")
            try:
                task_id = int(parts[2])
                new_status = database.toggle_task_status(task_id)
                stats = database.get_stats()
                self.send_json({"status": "toggled", "new_status": new_status, "stats": stats})
            except Exception as e:
                self.send_json({"error": str(e)}, 400)

        else:
            self.send_response(404)
            self.end_headers()

    def do_DELETE(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        if path.startswith("/api/tasks/"):
            parts = path.strip("/").split("/")
            try:
                task_id = int(parts[2])
                database.delete_task(task_id)
                self.send_json({"status": "deleted"})
            except Exception as e:
                self.send_json({"error": str(e)}, 400)
        else:
            self.send_response(404)
            self.end_headers()

def run_server():
    database.init_db()
    server_address = ("", PORT)
    httpd = HTTPServer(server_address, TimeWiseHandler)
    print(f"============================================================")
    print(f" TimeWise: Intelligent Productivity & Task Scheduling System")
    print(f" Python Backend & SQLite Database running at: http://localhost:{PORT}")
    print(f"============================================================")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server.")
        httpd.server_close()

if __name__ == "__main__":
    run_server()
