"""
TimeWise - Smart Scheduling Engine (Python)
Arranges tasks based on Priority, Deadline Date Urgency, and Available Work Time.
"""

from datetime import datetime, date

def parse_time_to_minutes(time_str):
    if not time_str:
        return 9 * 60
    parts = time_str.split(":")
    return int(parts[0]) * 60 + int(parts[1])

def minutes_to_clock(minutes_from_midnight):
    mins = ((minutes_from_midnight % (24 * 60)) + (24 * 60)) % (24 * 60)
    hrs24 = mins // 60
    m = mins % 60
    period = "PM" if hrs24 >= 12 else "AM"
    h12 = hrs24 % 12
    if h12 == 0:
        h12 = 12
    return f"{h12:02d}:{m:02d} {period}"

def format_duration(minutes):
    hrs = minutes // 60
    mins = minutes % 60
    if hrs > 0 and mins > 0:
        return f"{hrs}h {mins}m"
    elif hrs > 0:
        return f"{hrs}h"
    return f"{mins}m"

def compute_days_until_deadline(deadline_date_str):
    if not deadline_date_str:
        return 999
    try:
        dl_date = datetime.strptime(deadline_date_str, "%Y-%m-%d").date()
        today = date.today()
        diff = (dl_date - today).days
        return diff
    except Exception:
        return 999

def smart_schedule(tasks, available_minutes, day_start_str="09:00"):
    """
    Arranges tasks intelligently based on:
    1. Priority weighting (High=3, Medium=2, Low=1)
    2. Deadline Date proximity (Due Today/Tomorrow has highest urgency)
    3. Available daily study/work time constraint
    """
    day_start_mins = parse_time_to_minutes(day_start_str)

    pending_tasks = [t for t in tasks if t.get("status") != "Completed"]
    completed_tasks = [t for t in tasks if t.get("status") == "Completed"]

    p_weights = {"High": 3, "Medium": 2, "Low": 1}

    def compute_score(t):
        p_val = p_weights.get(t.get("priority", "Medium"), 2) * 50
        urgency = 0
        if t.get("has_deadline") and t.get("deadline_date"):
            days_left = compute_days_until_deadline(t.get("deadline_date"))
            if days_left <= 0:
                urgency = 60 # Due today or overdue!
            elif days_left == 1:
                urgency = 40 # Due tomorrow!
            elif days_left <= 3:
                urgency = 25 # Due within 3 days
            else:
                urgency = 10
        efficiency = (p_val * 20 // max(15, t.get("duration", 30)))
        return p_val + urgency + efficiency

    # Sort pending tasks by score descending
    sorted_pending = sorted(pending_tasks, key=compute_score, reverse=True)

    scheduled = []
    deferred = []

    # Completed tasks placed at start
    comp_time_offset = 0
    final_schedule = []

    for ct in completed_tasks:
        start_clock = minutes_to_clock(day_start_mins + comp_time_offset)
        end_clock = minutes_to_clock(day_start_mins + comp_time_offset + ct.get("duration", 30))
        comp_time_offset += ct.get("duration", 30)
        task_copy = dict(ct)
        task_copy["scheduled_start"] = start_clock
        task_copy["scheduled_end"] = end_clock
        task_copy["start_offset"] = comp_time_offset - ct.get("duration", 30)
        task_copy["end_offset"] = comp_time_offset
        final_schedule.append(task_copy)

    remaining_avail = max(0, available_minutes - comp_time_offset)
    current_time_offset = comp_time_offset

    for t in sorted_pending:
        dur = t.get("duration", 30)
        if (current_time_offset - comp_time_offset) + dur <= remaining_avail:
            start_clock = minutes_to_clock(day_start_mins + current_time_offset)
            end_clock = minutes_to_clock(day_start_mins + current_time_offset + dur)

            task_copy = dict(t)
            task_copy["scheduled_start"] = start_clock
            task_copy["scheduled_end"] = end_clock
            task_copy["start_offset"] = current_time_offset
            task_copy["end_offset"] = current_time_offset + dur
            scheduled.append(task_copy)
            final_schedule.append(task_copy)
            current_time_offset += dur
        else:
            task_copy = dict(t)
            task_copy["reason"] = f"Requires {format_duration(dur)}, only {format_duration(max(0, remaining_avail - (current_time_offset - comp_time_offset)))} left in daily work window."
            deferred.append(task_copy)

    total_allocated = current_time_offset
    utilization_pct = round((total_allocated / available_minutes * 100), 1) if available_minutes > 0 else 0

    return {
        "scheduled_tasks": final_schedule,
        "deferred_tasks": deferred,
        "total_allocated_minutes": total_allocated,
        "total_allocated_formatted": format_duration(total_allocated),
        "available_minutes": available_minutes,
        "available_formatted": format_duration(available_minutes),
        "utilization_percent": min(100.0, utilization_pct),
        "total_pending_scheduled": len(scheduled),
        "total_deferred": len(deferred)
    }
