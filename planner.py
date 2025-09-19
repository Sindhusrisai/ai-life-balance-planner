# planner.py
from datetime import datetime
import math

def parse_deadline(s):
    try:
        return datetime.fromisoformat(s)
    except:
        # allow YYYY-MM-DD or simple date
        try:
            return datetime.strptime(s, "%Y-%m-%d")
        except:
            return None

def score_task(task, energy_level):
    # basic scoring: urgency + priority + energy match
    urgency = 0.2
    dl = parse_deadline(task.get("deadline", "") or "")
    if dl:
        days_left = max(0, (dl.date() - datetime.now().date()).days)
        urgency = 1.0 if days_left == 0 else max(0.1, 1.0/(days_left+1))
    importance = (task.get("priority", 3) / 5.0)
    energy_match = 1.0 if task.get("energy_required","medium").lower() == energy_level.lower() else 0.6
    time_factor = math.log(1 + task.get("duration",30)) / math.log(1 + 60)
    score = 0.5*urgency + 0.3*importance + 0.15*energy_match + 0.05*time_factor
    return score

def prioritize_tasks(tasks, energy_level="medium"):
    # tasks: list of dicts with keys name,duration,deadline,priority,energy_required,category
    scored = []
    for t in tasks:
        sc = score_task(t, energy_level)
        scored.append((sc, t))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [t for sc,t in scored]

def generate_day_plan(tasks, availability_slots, energy_level="medium"):
    """
    availability_slots: list of tuples [("09:00","12:00"), ("15:00","18:00")]
    returns list of allocations: {title, minutes, start_slot}
    """
    # flatten available minutes
    slots = []
    for s,e in availability_slots:
        # convert to minutes available
        sh, sm = map(int, s.split(":"))
        eh, em = map(int, e.split(":"))
        total = (eh*60+em) - (sh*60+sm)
        if total > 0:
            slots.append({"start": s, "minutes": total})
    plan = []
    prioritized = prioritize_tasks(tasks, energy_level)
    for task in prioritized:
        remaining = task.get("duration", 30)
        for slot in slots:
            if remaining <= 0:
                break
            if slot["minutes"] <= 0:
                continue
            take = min(remaining, slot["minutes"], 60)  # chunk cap 60
            plan.append({"title": task["name"], "minutes": int(take), "slot_start": slot["start"], "category": task.get("category","")})
            slot["minutes"] -= take
            remaining -= take
    return plan
