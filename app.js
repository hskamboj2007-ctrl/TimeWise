/**
 * TimeWise - Frontend Interactive Controller
 * Connects HTML UI to Python/SQLite Backend
 * Features: Plant Growth Visualization, Weekly/Monthly Line Chart, Smart Scheduling
 */

const API_BASE = window.location.origin.startsWith("http") ? window.location.origin : "http://localhost:5000";

// Helper: Format Date string (YYYY-MM-DD) into readable format
function formatDeadlineDisplay(dateStr) {
    if (!dateStr) return "No Deadline";
    try {
        const parts = dateStr.split("-");
        const dl = new Date(parseInt(parts[0]), parseInt(parts[1]) - 1, parseInt(parts[2]));
        const now = new Date();
        const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
        const diffDays = Math.round((dl - today) / (1000 * 60 * 60 * 24));

        const months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
        const formatted = `${months[dl.getMonth()]} ${dl.getDate()}`;

        if (diffDays === 0) return `Due: Today (${formatted})`;
        if (diffDays === 1) return `Due: Tomorrow (${formatted})`;
        if (diffDays < 0) return `Overdue: ${formatted}`;
        return `Due: ${formatted}`;
    } catch (e) {
        return `Due: ${dateStr}`;
    }
}

function parseTimeToMinutes(timeStr) {
    if (!timeStr) return 9 * 60;
    const parts = timeStr.split(":");
    return (parseInt(parts[0]) || 0) * 60 + (parseInt(parts[1]) || 0);
}

function minutesToClock(minutesFromMidnight) {
    let mins = ((minutesFromMidnight % (24 * 60)) + (24 * 60)) % (24 * 60);
    const hrs24 = Math.floor(mins / 60);
    const m = mins % 60;
    const period = hrs24 >= 12 ? "PM" : "AM";
    let h12 = hrs24 % 12;
    if (h12 === 0) h12 = 12;
    const pad = (n) => (n < 10 ? "0" + n : n);
    return `${pad(h12)}:${pad(m)} ${period}`;
}

function formatDuration(minutes) {
    const hrs = Math.floor(minutes / 60);
    const mins = minutes % 60;
    if (hrs > 0 && mins > 0) return `${hrs}h ${mins}m`;
    if (hrs > 0) return `${hrs}h`;
    return `${mins}m`;
}

// Fallback in-memory state if server is not reachable
const todayIso = new Date().toISOString().split("T")[0];
const tomorrowIso = new Date(Date.now() + 86400000).toISOString().split("T")[0];
const nextWeekIso = new Date(Date.now() + 86400000 * 3).toISOString().split("T")[0];

let localTasks = [
    { id: 1, title: "Machine Learning", duration: 90, priority: "High", has_deadline: 1, deadline_date: todayIso, scheduled_start: "10:00 AM", scheduled_end: "11:30 AM", status: "Pending", category: "Study" },
    { id: 2, title: "DBMS Assignment", duration: 60, priority: "Medium", has_deadline: 1, deadline_date: tomorrowIso, scheduled_start: "12:00 PM", scheduled_end: "01:00 PM", status: "Pending", category: "Assignment" },
    { id: 3, title: "Project Work", duration: 120, priority: "Low", has_deadline: 1, deadline_date: nextWeekIso, scheduled_start: "04:00 PM", scheduled_end: "06:00 PM", status: "Pending", category: "Project" },
    { id: 4, title: "Algorithm Practice", duration: 45, priority: "High", has_deadline: 1, deadline_date: todayIso, scheduled_start: "02:00 PM", scheduled_end: "02:45 PM", status: "Completed", category: "Coding" },
    { id: 5, title: "Read Research Paper", duration: 30, priority: "Medium", has_deadline: 0, deadline_date: "", scheduled_start: "03:00 PM", scheduled_end: "03:30 PM", status: "Completed", category: "Reading" },
    { id: 6, title: "System Design Revision", duration: 45, priority: "High", has_deadline: 1, deadline_date: tomorrowIso, scheduled_start: "05:00 PM", scheduled_end: "05:45 PM", status: "Completed", category: "Study" },
    { id: 7, title: "Review Pull Requests", duration: 20, priority: "Low", has_deadline: 0, deadline_date: "", scheduled_start: "06:00 PM", scheduled_end: "06:20 PM", status: "Completed", category: "Work" },
    { id: 8, title: "Daily Notes Journaling", duration: 15, priority: "Low", has_deadline: 0, deadline_date: "", scheduled_start: "06:30 PM", scheduled_end: "06:45 PM", status: "Completed", category: "Personal" }
];

let isServerConnected = false;
let currentChartMode = "weekly";
let historyData = null;

// DOM Elements
const greetingHeading = document.getElementById("greetingHeading");
const statTotalTasks = document.getElementById("statTotalTasks");
const statCompleted = document.getElementById("statCompleted");
const statPending = document.getElementById("statPending");
const statProgress = document.getElementById("statProgress");
const tasksListContainer = document.getElementById("tasksListContainer");
const quickAddTrigger = document.getElementById("quickAddTrigger");
const btnOpenAddTask = document.getElementById("btnOpenAddTask");
const addTaskModal = document.getElementById("addTaskModal");
const btnCloseModal = document.getElementById("btnCloseModal");
const btnCancelModal = document.getElementById("btnCancelModal");
const addTaskForm = document.getElementById("addTaskForm");
const taskHasDeadline = document.getElementById("taskHasDeadline");
const deadlineContainer = document.getElementById("deadlineContainer");
const taskDeadlineDate = document.getElementById("taskDeadlineDate");
const btnSmartSchedule = document.getElementById("btnSmartSchedule");
const scheduleTimeline = document.getElementById("scheduleTimeline");
const deferredTasksBox = document.getElementById("deferredTasksBox");
const deferredTasksList = document.getElementById("deferredTasksList");
const workWindowSelect = document.getElementById("workWindowSelect");
const plantSvgWrapper = document.getElementById("plantSvgWrapper");
const plantProgressFill = document.getElementById("plantProgressFill");
const plantStatusText = document.getElementById("plantStatusText");
const plantStageBadge = document.getElementById("plantStageBadge");
const celebrationToast = document.getElementById("celebrationToast");
const toastTitle = document.getElementById("toastTitle");
const toastMessage = document.getElementById("toastMessage");
const productivityChart = document.getElementById("productivityChart");
const chartTooltip = document.getElementById("chartTooltip");
const btnWeekly = document.getElementById("btnWeekly");
const btnMonthly = document.getElementById("btnMonthly");

// ==========================================
// 1. DYNAMIC TIME-BASED GREETING
// ==========================================
function updateGreeting() {
    const hour = new Date().getHours();
    if (hour >= 5 && hour < 12) {
        greetingHeading.textContent = "Good morning!";
    } else if (hour >= 12 && hour < 17) {
        greetingHeading.textContent = "Good afternoon!";
    } else if (hour >= 17 && hour < 22) {
        greetingHeading.textContent = "Good evening!";
    } else {
        greetingHeading.textContent = "Good night!";
    }
}

// ==========================================
// 2. DATA FETCHING & SYNCHRONIZATION
// ==========================================
async function checkServer() {
    try {
        const res = await fetch(`${API_BASE}/api/stats`);
        if (res.ok) {
            isServerConnected = true;
            return true;
        }
    } catch (e) {
        isServerConnected = false;
    }
    return false;
}

async function fetchTasks() {
    if (isServerConnected) {
        try {
            const res = await fetch(`${API_BASE}/api/tasks`);
            const data = await res.json();
            return data.tasks || [];
        } catch (e) {
            console.warn("Server task fetch failed, using local fallback", e);
        }
    }
    return localTasks;
}

async function fetchStats() {
    if (isServerConnected) {
        try {
            const res = await fetch(`${API_BASE}/api/stats`);
            return await res.json();
        } catch (e) {
            console.warn("Server stats fetch failed", e);
        }
    }
    const total = localTasks.length;
    const completed = localTasks.filter(t => t.status === "Completed").length;
    const pending = total - completed;
    const progress = total > 0 ? Math.round((completed / total) * 100) : 0;
    
    let stage = 0;
    let sName = "Seed in Soil";
    let pDesc = "Complete your first task to sprout the seed!";
    if (progress >= 100) {
        stage = 5; sName = "Fully Bloomed!"; pDesc = "All tasks completed! Your plant is in full blossom 🌺✨";
    } else if (progress >= 75) {
        stage = 4; sName = "Budding Flower"; pDesc = "Almost there! Flower buds are ready to bloom 🌸";
    } else if (progress >= 50) {
        stage = 3; sName = "Lush Foliage"; pDesc = "Flourishing with multiple vibrant leaves 🍃";
    } else if (progress >= 25) {
        stage = 2; sName = "Seedling"; pDesc = "Growing strong with fresh leaves 🌿";
    } else if (progress > 0) {
        stage = 1; sName = "Sprout"; pDesc = "A small green sprout has emerged 🌱";
    }

    return {
        total, completed, pending, progress,
        plant_stage: stage,
        stage_name: sName,
        plant_desc: pDesc
    };
}

// Client-side fallback Smart Scheduler (always guarantees output!)
function clientSmartSchedule(taskList, availMins = 360, dayStartStr = "09:00") {
    const startMins = parseTimeToMinutes(dayStartStr);
    const pending = taskList.filter(t => t.status !== "Completed");
    const completed = taskList.filter(t => t.status === "Completed");

    const pWeights = { High: 3, Medium: 2, Low: 1 };
    pending.sort((a, b) => {
        const pDiff = (pWeights[b.priority] || 2) - (pWeights[a.priority] || 2);
        if (pDiff !== 0) return pDiff;
        return (a.duration || 30) - (b.duration || 30);
    });

    const scheduled = [];
    const deferred = [];
    let curOffset = 0;

    // Completed tasks placed first
    completed.forEach(ct => {
        const dur = ct.duration || 30;
        scheduled.push({
            ...ct,
            scheduled_start: minutesToClock(startMins + curOffset),
            scheduled_end: minutesToClock(startMins + curOffset + dur)
        });
        curOffset += dur;
    });

    const remAvail = Math.max(0, availMins - curOffset);
    let pendOffset = curOffset;

    pending.forEach(pt => {
        const dur = pt.duration || 30;
        if ((pendOffset - curOffset) + dur <= remAvail) {
            scheduled.push({
                ...pt,
                scheduled_start: minutesToClock(startMins + pendOffset),
                scheduled_end: minutesToClock(startMins + pendOffset + dur)
            });
            pendOffset += dur;
        } else {
            deferred.push({
                ...pt,
                reason: `Requires ${formatDuration(dur)}, only ${formatDuration(Math.max(0, remAvail - (pendOffset - curOffset)))} left in daily window.`
            });
        }
    });

    return {
        scheduled_tasks: scheduled,
        deferred_tasks: deferred,
        available_minutes: availMins,
        total_allocated_minutes: pendOffset
    };
}

async function fetchSchedule() {
    const availMins = workWindowSelect ? parseInt(workWindowSelect.value) || 360 : 360;
    if (isServerConnected) {
        try {
            const res = await fetch(`${API_BASE}/api/schedule`);
            if (res.ok) {
                return await res.json();
            }
        } catch (e) {
            console.warn("Server schedule fetch failed, running local scheduler", e);
        }
    }
    // Reliable fallback scheduler
    const tasks = await fetchTasks();
    return clientSmartSchedule(tasks, availMins, "09:00");
}

async function fetchHistory() {
    if (isServerConnected) {
        try {
            const res = await fetch(`${API_BASE}/api/history`);
            return await res.json();
        } catch (e) {
            console.warn("Server history fetch failed", e);
        }
    }
    return {
        weekly: [
            { day_name: "Mon", completed_count: 4, total_count: 6, focus_minutes: 180 },
            { day_name: "Tue", completed_count: 6, total_count: 7, focus_minutes: 240 },
            { day_name: "Wed", completed_count: 5, total_count: 8, focus_minutes: 210 },
            { day_name: "Thu", completed_count: 7, total_count: 8, focus_minutes: 270 },
            { day_name: "Fri", completed_count: 5, total_count: 6, focus_minutes: 200 },
            { day_name: "Sat", completed_count: 3, total_count: 5, focus_minutes: 120 },
            { day_name: "Sun", completed_count: 5, total_count: 8, focus_minutes: 220 }
        ],
        monthly: [
            { label: "Week 1", completed: 24, total: 32, rate: 75 },
            { label: "Week 2", completed: 28, total: 35, rate: 80 },
            { label: "Week 3", completed: 31, total: 36, rate: 86 },
            { label: "Week 4", completed: 35, total: 40, rate: 88 }
        ]
    };
}

// ==========================================
// 3. UI RENDERING: STAT CARDS & TASK LIST
// ==========================================
function pad2(n) {
    return n < 10 ? "0" + n : n;
}

function renderStats(stats) {
    statTotalTasks.textContent = pad2(stats.total);
    statCompleted.textContent = pad2(stats.completed);
    statPending.textContent = pad2(stats.pending);
    statProgress.textContent = `${stats.progress}%`;

    plantStageBadge.textContent = stats.stage_name;
    plantProgressFill.style.width = `${stats.progress}%`;
    plantStatusText.innerHTML = `${stats.progress}% Growth &bull; ${stats.plant_desc}`;

    renderPlantSvg(stats.plant_stage, stats.progress);
}

function renderTasks(tasks) {
    tasksListContainer.innerHTML = "";

    if (tasks.length === 0) {
        tasksListContainer.innerHTML = `
            <div style="text-align:center; padding: 24px; color:#94a3b8; font-size:14px;">
                No tasks yet. Click "+ Add a new task" to get started!
            </div>
        `;
        return;
    }

    tasks.forEach(t => {
        const item = document.createElement("div");
        const isComp = t.status === "Completed";
        item.className = `task-item ${isComp ? "is-completed" : ""}`;

        let timeLabel = t.scheduled_start || "10:00 AM";
        let deadlineLabel = "";

        if (t.has_deadline && t.deadline_date) {
            deadlineLabel = `<span style="color:#d97706; font-weight:600;"> • 📅 ${formatDeadlineDisplay(t.deadline_date)}</span>`;
        } else if (t.has_deadline) {
            deadlineLabel = `<span style="color:#d97706; font-weight:600;"> • 📅 Due Soon</span>`;
        } else {
            deadlineLabel = `<span style="color:#94a3b8;"> • No Deadline</span>`;
        }

        const pri = t.priority ? t.priority.toLowerCase() : "medium";

        item.innerHTML = `
            <div class="task-main-col">
                <button type="button" class="task-checkbox-btn" onclick="toggleTask(${t.id})">
                    ${isComp ? "✓" : ""}
                </button>
                <div class="task-info">
                    <span class="task-title">${escapeHtml(t.title)}</span>
                    <span class="task-time-meta">${timeLabel}${deadlineLabel}</span>
                </div>
            </div>
            <div class="task-end-col">
                <span class="priority-pill ${pri}">${t.priority}</span>
                <button type="button" class="btn-task-delete" title="Delete Task" onclick="deleteTask(${t.id})">✕</button>
            </div>
        `;
        tasksListContainer.appendChild(item);
    });
}

function escapeHtml(str) {
    if (!str) return "";
    return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

// ==========================================
// 4. PLANT GROWTH VISUALIZATION (SVG ENGINE)
// ==========================================
function renderPlantSvg(stage, progress) {
    const potSvg = `
        <g id="pot">
            <ellipse cx="100" cy="155" rx="36" ry="7" fill="#58311a" />
            <path d="M 60 152 Q 100 157 140 152 L 138 159 Q 100 164 62 159 Z" fill="#c26d45" />
            <path d="M 62 159 Q 100 164 138 159 L 126 195 Q 100 198 74 195 Z" fill="#d97745" />
            <path d="M 63 159 L 75 195 Q 85 197 95 196 L 85 160 Z" fill="rgba(255,255,255,0.15)" />
            <ellipse cx="100" cy="196" rx="28" ry="4" fill="#a4532b" />
        </g>
    `;

    let plantSvg = "";

    if (stage === 0) {
        plantSvg = `
            <svg viewBox="0 0 200 210" width="180" height="190" xmlns="http://www.w3.org/2000/svg">
                ${potSvg}
                <ellipse cx="100" cy="153" rx="4" ry="3" fill="#854d0e" />
                <path d="M 100 120 C 96 126 93 130 93 133 A 7 7 0 0 0 107 133 C 107 130 104 126 100 120 Z" fill="#38bdf8" opacity="0.8">
                    <animate attributeName="transform" type="translate" values="0,0; 0,15; 0,0" dur="2s" repeatCount="indefinite" />
                </path>
            </svg>
        `;
    } else if (stage === 1) {
        plantSvg = `
            <svg viewBox="0 0 200 210" width="180" height="190" xmlns="http://www.w3.org/2000/svg">
                ${potSvg}
                <path d="M 100 153 Q 99 142 100 135" stroke="#22c55e" stroke-width="3" fill="none" stroke-linecap="round" />
                <path d="M 100 135 Q 88 132 90 126 Q 96 128 100 135" fill="#4ade80" />
                <path d="M 100 135 Q 112 132 110 126 Q 104 128 100 135" fill="#22c55e" />
            </svg>
        `;
    } else if (stage === 2) {
        plantSvg = `
            <svg viewBox="0 0 200 210" width="180" height="190" xmlns="http://www.w3.org/2000/svg">
                ${potSvg}
                <path d="M 100 153 Q 102 130 100 115" stroke="#16a34a" stroke-width="3.5" fill="none" stroke-linecap="round" />
                <path d="M 100 138 Q 80 140 78 128 Q 92 128 100 138" fill="#4ade80" />
                <path d="M 100 132 Q 120 135 122 124 Q 108 122 100 132" fill="#22c55e" />
                <path d="M 100 115 Q 82 110 86 98 Q 97 104 100 115" fill="#86efac" />
                <path d="M 100 115 Q 118 110 114 98 Q 103 104 100 115" fill="#4ade80" />
            </svg>
        `;
    } else if (stage === 3) {
        plantSvg = `
            <svg viewBox="0 0 200 210" width="180" height="190" xmlns="http://www.w3.org/2000/svg">
                ${potSvg}
                <path d="M 100 153 Q 98 125 100 95" stroke="#15803d" stroke-width="4" fill="none" stroke-linecap="round" />
                <path d="M 100 130 Q 75 125 65 110" stroke="#15803d" stroke-width="2.5" fill="none" stroke-linecap="round" />
                <path d="M 100 118 Q 125 115 135 100" stroke="#15803d" stroke-width="2.5" fill="none" stroke-linecap="round" />
                <path d="M 65 110 Q 50 115 52 95 Q 68 100 65 110" fill="#22c55e" />
                <path d="M 135 100 Q 150 105 148 85 Q 132 90 135 100" fill="#16a34a" />
                <path d="M 99 120 Q 70 110 74 90 Q 92 102 99 120" fill="#4ade80" />
                <path d="M 100 108 Q 130 98 126 80 Q 108 92 100 108" fill="#22c55e" />
                <path d="M 100 95 Q 85 75 90 65 Q 100 78 100 95" fill="#86efac" />
                <path d="M 100 95 Q 115 75 110 65 Q 100 78 100 95" fill="#4ade80" />
                <path d="M 100 95 Q 100 68 100 60 Q 105 75 100 95" fill="#22c55e" />
            </svg>
        `;
    } else if (stage === 4) {
        plantSvg = `
            <svg viewBox="0 0 200 210" width="180" height="190" xmlns="http://www.w3.org/2000/svg">
                ${potSvg}
                <path d="M 100 153 Q 101 115 100 80" stroke="#15803d" stroke-width="4" fill="none" stroke-linecap="round" />
                <path d="M 100 125 Q 70 115 60 98" stroke="#15803d" stroke-width="3" fill="none" stroke-linecap="round" />
                <path d="M 100 110 Q 130 100 140 85" stroke="#15803d" stroke-width="3" fill="none" stroke-linecap="round" />
                <path d="M 60 98 Q 42 102 45 84 Q 62 88 60 98" fill="#22c55e" />
                <path d="M 140 85 Q 158 90 155 72 Q 138 76 140 85" fill="#16a34a" />
                <path d="M 100 115 Q 75 100 80 78 Q 98 90 100 115" fill="#4ade80" />
                <path d="M 100 100 Q 125 85 120 65 Q 105 78 100 100" fill="#22c55e" />
                <ellipse cx="60" cy="85" rx="5" ry="7" fill="#f43f5e" transform="rotate(-15 60 85)" />
                <ellipse cx="140" cy="73" rx="5" ry="7" fill="#f43f5e" transform="rotate(15 140 73)" />
                <ellipse cx="100" cy="74" rx="7" ry="10" fill="#fb7185" />
                <ellipse cx="100" cy="70" rx="4" ry="7" fill="#fda4af" />
            </svg>
        `;
    } else {
        plantSvg = `
            <svg viewBox="0 0 200 210" width="180" height="190" xmlns="http://www.w3.org/2000/svg">
                ${potSvg}
                <path d="M 100 153 Q 98 115 100 78" stroke="#15803d" stroke-width="4.5" fill="none" stroke-linecap="round" />
                <path d="M 100 125 Q 65 115 55 90" stroke="#15803d" stroke-width="3" fill="none" stroke-linecap="round" />
                <path d="M 100 110 Q 135 102 145 78" stroke="#15803d" stroke-width="3" fill="none" stroke-linecap="round" />
                <path d="M 55 90 Q 36 94 40 76 Q 57 80 55 90" fill="#22c55e" />
                <path d="M 145 78 Q 164 82 160 64 Q 142 68 145 78" fill="#16a34a" />
                <path d="M 100 112 Q 74 95 78 72 Q 97 86 100 112" fill="#4ade80" />
                <path d="M 100 95 Q 128 78 122 56 Q 104 70 100 95" fill="#22c55e" />

                <g transform="translate(55, 78) scale(0.65)">
                    <circle cx="0" cy="-12" r="9" fill="#f43f5e" />
                    <circle cx="12" cy="0" r="9" fill="#f43f5e" />
                    <circle cx="0" cy="12" r="9" fill="#f43f5e" />
                    <circle cx="-12" cy="0" r="9" fill="#f43f5e" />
                    <circle cx="0" cy="0" r="6" fill="#fef08a" />
                </g>

                <g transform="translate(145, 66) scale(0.65)">
                    <circle cx="0" cy="-12" r="9" fill="#f43f5e" />
                    <circle cx="12" cy="0" r="9" fill="#f43f5e" />
                    <circle cx="0" cy="12" r="9" fill="#f43f5e" />
                    <circle cx="-12" cy="0" r="9" fill="#f43f5e" />
                    <circle cx="0" cy="0" r="6" fill="#fef08a" />
                </g>

                <g transform="translate(100, 62)">
                    <circle cx="0" cy="-16" r="12" fill="#fb7185" />
                    <circle cx="15" cy="-5" r="12" fill="#f43f5e" />
                    <circle cx="9" cy="14" r="12" fill="#fb7185" />
                    <circle cx="-9" cy="14" r="12" fill="#f43f5e" />
                    <circle cx="-15" cy="-5" r="12" fill="#fb7185" />
                    <circle cx="0" cy="0" r="9" fill="#fde047" />
                    <circle cx="0" cy="0" r="5" fill="#ea580c" />
                </g>

                <circle cx="65" cy="48" r="2.5" fill="#facc15">
                    <animate attributeName="opacity" values="0.3;1;0.3" dur="1.5s" repeatCount="indefinite" />
                </circle>
                <circle cx="135" cy="40" r="2" fill="#facc15">
                    <animate attributeName="opacity" values="1;0.2;1" dur="1.8s" repeatCount="indefinite" />
                </circle>
                <circle cx="100" cy="28" r="3" fill="#facc15">
                    <animate attributeName="opacity" values="0.5;1;0.5" dur="1.2s" repeatCount="indefinite" />
                </circle>
            </svg>
        `;
    }

    plantSvgWrapper.innerHTML = plantSvg;
}

// ==========================================
// 5. REPORT GRAPH ANALYSIS (CANVAS LINE CHART)
// ==========================================
function renderProductivityChart() {
    if (!historyData) return;
    const ctx = productivityChart.getContext("2d");
    const dpr = window.devicePixelRatio || 1;
    const width = productivityChart.parentElement.clientWidth || 450;
    const height = 200;

    productivityChart.width = width * dpr;
    productivityChart.height = height * dpr;
    ctx.scale(dpr, dpr);

    const isWeekly = currentChartMode === "weekly";
    const dataset = isWeekly ? historyData.weekly : historyData.monthly;

    const labels = dataset.map(d => isWeekly ? d.day_name : d.label);
    const rates = dataset.map(d => {
        if (d.rate !== undefined) return d.rate;
        return d.total_count > 0 ? Math.round((d.completed_count / d.total_count) * 100) : 0;
    });

    ctx.clearRect(0, 0, width, height);

    const padLeft = 40;
    const padRight = 20;
    const padTop = 25;
    const padBottom = 35;
    const chartW = width - padLeft - padRight;
    const chartH = height - padTop - padBottom;

    ctx.strokeStyle = "#f1f5f9";
    ctx.lineWidth = 1;
    ctx.fillStyle = "#94a3b8";
    ctx.font = "500 11px Plus Jakarta Sans, sans-serif";
    ctx.textAlign = "right";

    const yLevels = [0, 25, 50, 75, 100];
    yLevels.forEach(lvl => {
        const y = padTop + chartH - (lvl / 100) * chartH;
        ctx.beginPath();
        ctx.moveTo(padLeft, y);
        ctx.lineTo(width - padRight, y);
        ctx.stroke();
        ctx.fillText(`${lvl}%`, padLeft - 8, y + 4);
    });

    if (labels.length < 2) return;

    const stepX = chartW / (labels.length - 1);
    const points = rates.map((r, i) => ({
        x: padLeft + i * stepX,
        y: padTop + chartH - (r / 100) * chartH,
        rate: r,
        label: labels[i],
        raw: dataset[i]
    }));

    const gradient = ctx.createLinearGradient(0, padTop, 0, padTop + chartH);
    gradient.addColorStop(0, "rgba(37, 99, 235, 0.22)");
    gradient.addColorStop(1, "rgba(37, 99, 235, 0.0)");

    ctx.beginPath();
    ctx.moveTo(points[0].x, padTop + chartH);
    ctx.lineTo(points[0].x, points[0].y);

    for (let i = 0; i < points.length - 1; i++) {
        const xc = (points[i].x + points[i + 1].x) / 2;
        const yc = (points[i].y + points[i + 1].y) / 2;
        ctx.quadraticCurveTo(points[i].x, points[i].y, xc, yc);
    }
    const last = points[points.length - 1];
    ctx.lineTo(last.x, last.y);
    ctx.lineTo(last.x, padTop + chartH);
    ctx.closePath();
    ctx.fillStyle = gradient;
    ctx.fill();

    ctx.beginPath();
    ctx.moveTo(points[0].x, points[0].y);
    for (let i = 0; i < points.length - 1; i++) {
        const xc = (points[i].x + points[i + 1].x) / 2;
        const yc = (points[i].y + points[i + 1].y) / 2;
        ctx.quadraticCurveTo(points[i].x, points[i].y, xc, yc);
    }
    ctx.lineTo(last.x, last.y);
    ctx.strokeStyle = "#2563eb";
    ctx.lineWidth = 3;
    ctx.stroke();

    ctx.textAlign = "center";
    points.forEach(p => {
        ctx.beginPath();
        ctx.arc(p.x, p.y, 5, 0, Math.PI * 2);
        ctx.fillStyle = "#ffffff";
        ctx.fill();
        ctx.strokeStyle = "#2563eb";
        ctx.lineWidth = 2.5;
        ctx.stroke();

        ctx.fillStyle = "#64748b";
        ctx.fillText(p.label, p.x, height - 10);
    });

    productivityChart._points = points;
}

productivityChart.addEventListener("mousemove", (e) => {
    if (!productivityChart._points) return;
    const rect = productivityChart.getBoundingClientRect();
    const mouseX = e.clientX - rect.left;
    const mouseY = e.clientY - rect.top;

    let closest = null;
    let minDist = 30;

    productivityChart._points.forEach(p => {
        const dist = Math.hypot(p.x - mouseX, p.y - mouseY);
        if (dist < minDist) {
            minDist = dist;
            closest = p;
        }
    });

    if (closest) {
        chartTooltip.style.display = "block";
        chartTooltip.style.left = `${closest.x}px`;
        chartTooltip.style.top = `${closest.y}px`;
        const raw = closest.raw;
        const comp = raw.completed_count !== undefined ? raw.completed_count : raw.completed;
        const tot = raw.total_count !== undefined ? raw.total_count : raw.total;
        chartTooltip.innerHTML = `<strong>${closest.label}</strong>: ${closest.rate}% (${comp}/${tot} tasks)`;
    } else {
        chartTooltip.style.display = "none";
    }
});

productivityChart.addEventListener("mouseleave", () => {
    chartTooltip.style.display = "none";
});

btnWeekly.addEventListener("click", () => {
    btnWeekly.classList.add("active");
    btnMonthly.classList.remove("active");
    currentChartMode = "weekly";
    renderProductivityChart();
});

btnMonthly.addEventListener("click", () => {
    btnMonthly.classList.add("active");
    btnWeekly.classList.remove("active");
    currentChartMode = "monthly";
    renderProductivityChart();
});

// ==========================================
// 6. DAILY PLANNER TIMELINE (SMART SCHEDULE)
// ==========================================
function renderDailySchedule(scheduleData) {
    if (!scheduleData || !scheduleData.scheduled_tasks) {
        scheduleTimeline.innerHTML = `
            <div style="text-align:center; padding: 24px; color:#94a3b8; font-size:14px;">
                No tasks scheduled yet. Click <strong>"⚡ Smart Schedule"</strong> above!
            </div>
        `;
        return;
    }

    scheduleTimeline.innerHTML = "";

    if (scheduleData.scheduled_tasks.length === 0) {
        scheduleTimeline.innerHTML = `
            <div style="text-align:center; padding: 24px; color:#94a3b8; font-size:14px;">
                No tasks scheduled yet. Click <strong>"⚡ Smart Schedule"</strong> above!
            </div>
        `;
        return;
    }

    if (workWindowSelect && scheduleData.available_minutes) {
        workWindowSelect.value = scheduleData.available_minutes;
    }

    scheduleData.scheduled_tasks.forEach(st => {
        const slot = document.createElement("div");
        const pri = st.priority ? st.priority.toLowerCase() : "medium";
        const isComp = st.status === "Completed";

        const startStr = st.scheduled_start || "09:00 AM";
        const endStr = st.scheduled_end || "10:00 AM";
        const durStr = formatDuration(st.duration || 30);
        const dlStr = (st.has_deadline && st.deadline_date) ? ` &bull; 📅 Due: ${st.deadline_date}` : "";

        slot.className = `timeline-slot ${pri} ${isComp ? "completed" : ""}`;
        slot.innerHTML = `
            <div class="slot-time-range">${startStr} - ${endStr}</div>
            <div class="slot-details">
                <div class="slot-title">${escapeHtml(st.title)} (${durStr})</div>
                <div class="slot-meta">Priority: <strong>${st.priority}</strong>${dlStr} &bull; ${isComp ? "✓ Completed" : "Planned"}</div>
            </div>
        `;
        scheduleTimeline.appendChild(slot);
    });

    if (scheduleData.deferred_tasks && scheduleData.deferred_tasks.length > 0) {
        deferredTasksBox.style.display = "block";
        deferredTasksList.innerHTML = "";
        scheduleData.deferred_tasks.forEach(dt => {
            const li = document.createElement("li");
            li.innerHTML = `&bull; <strong>${escapeHtml(dt.title)}</strong> (${formatDuration(dt.duration || 30)}, Priority: ${dt.priority}) - ${dt.reason || "Exceeds daily work window"}`;
            deferredTasksList.appendChild(li);
        });
    } else {
        deferredTasksBox.style.display = "none";
    }
}

// ==========================================
// 7. TASK ACTIONS: TOGGLE, ADD, DELETE
// ==========================================
window.toggleTask = async function(id) {
    let newStatus = "Completed";
    if (isServerConnected) {
        try {
            const res = await fetch(`${API_BASE}/api/tasks/${id}/toggle`, { method: "POST" });
            const data = await res.json();
            newStatus = data.new_status;
        } catch (e) {
            console.warn("Failed to toggle on server", e);
        }
    } else {
        const t = localTasks.find(item => item.id === id);
        if (t) {
            t.status = t.status === "Completed" ? "Pending" : "Completed";
            newStatus = t.status;
        }
    }

    if (newStatus === "Completed") {
        showCelebrationToast("Task Completed! 🌱", "Your plant absorbed productivity nutrients and grew!");
    }

    await reloadAll();
};

window.deleteTask = async function(id) {
    if (!confirm("Delete this task?")) return;
    if (isServerConnected) {
        try {
            await fetch(`${API_BASE}/api/tasks/${id}`, { method: "DELETE" });
        } catch (e) {
            console.warn("Failed to delete on server", e);
        }
    } else {
        localTasks = localTasks.filter(item => item.id !== id);
    }
    await reloadAll();
};

function showCelebrationToast(title, msg) {
    toastTitle.textContent = title;
    toastMessage.textContent = msg;
    celebrationToast.classList.add("show");
    setTimeout(() => {
        celebrationToast.classList.remove("show");
    }, 3200);
}

function openModal() {
    addTaskModal.classList.add("active");
    const today = new Date().toISOString().split("T")[0];
    taskDeadlineDate.value = today;
}

function closeModal() {
    addTaskModal.classList.remove("active");
    addTaskForm.reset();
}

btnOpenAddTask.addEventListener("click", openModal);
quickAddTrigger.addEventListener("click", openModal);
btnCloseModal.addEventListener("click", closeModal);
btnCancelModal.addEventListener("click", closeModal);

taskHasDeadline.addEventListener("change", () => {
    if (taskHasDeadline.value === "no") {
        deadlineContainer.style.display = "none";
    } else {
        deadlineContainer.style.display = "block";
    }
});

addTaskForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const title = document.getElementById("taskTitleInput").value.trim();
    const hrs = parseInt(document.getElementById("taskHours").value) || 0;
    const mins = parseInt(document.getElementById("taskMins").value) || 0;
    const duration = Math.max(10, hrs * 60 + mins);
    const priority = document.getElementById("taskPriorityInput").value;
    const hasDl = taskHasDeadline.value === "yes";
    const dlDate = hasDl ? taskDeadlineDate.value : "";
    const category = document.getElementById("taskCategory").value;

    const payload = {
        title: title,
        duration: duration,
        priority: priority,
        has_deadline: hasDl,
        deadline_date: dlDate,
        category: category
    };

    if (isServerConnected) {
        try {
            await fetch(`${API_BASE}/api/tasks`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });
        } catch (e) {
            console.warn("Failed to add task on server", e);
        }
    } else {
        payload.id = Date.now();
        payload.status = "Pending";
        localTasks.push(payload);
    }

    closeModal();
    showCelebrationToast("New Task Planted! 🌰", "Now scheduled in your productivity plan.");
    await reloadAll();
});

btnSmartSchedule.addEventListener("click", async () => {
    if (isServerConnected) {
        try {
            const res = await fetch(`${API_BASE}/api/smart-schedule`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({})
            });
            const data = await res.json();
            renderDailySchedule(data);
            showCelebrationToast("Smart AI Scheduling Run ⚡", `Arranged tasks based on priority and deadline dates.`);
            await reloadAll();
            return;
        } catch (e) {
            console.warn("Smart schedule API error", e);
        }
    }
    const tasks = await fetchTasks();
    const sched = clientSmartSchedule(tasks, 360, "09:00");
    renderDailySchedule(sched);
    showCelebrationToast("Smart Schedule Updated ⚡", "Tasks balanced across your daily window.");
});

// ==========================================
// 8. INITIALIZATION & REFRESH
// ==========================================
async function reloadAll() {
    const tasks = await fetchTasks();
    const stats = await fetchStats();
    renderStats(stats);
    renderTasks(tasks);

    const schedule = await fetchSchedule();
    if (schedule) {
        renderDailySchedule(schedule);
    }
}

if (workWindowSelect) {
    workWindowSelect.addEventListener("change", async () => {
        const mins = parseInt(workWindowSelect.value) || 360;
        if (isServerConnected) {
            try {
                await fetch(`${API_BASE}/api/settings`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ available_minutes: mins })
                });
            } catch (e) {
                console.warn("Failed to update settings on server", e);
            }
        }
        showCelebrationToast("Work Window Updated ⏱️", `Set to ${formatDuration(mins)}. Rescheduling tasks!`);
        await reloadAll();
    });
}

async function init() {
    updateGreeting();
    await checkServer();
    if (isServerConnected) {
        try {
            const res = await fetch(`${API_BASE}/api/settings`);
            if (res.ok) {
                const s = await res.json();
                if (s.available_minutes && workWindowSelect) {
                    workWindowSelect.value = s.available_minutes;
                }
            }
        } catch (e) {}
    }
    historyData = await fetchHistory();
    await reloadAll();
    renderProductivityChart();
    window.addEventListener("resize", renderProductivityChart);
}

window.addEventListener("DOMContentLoaded", init);
