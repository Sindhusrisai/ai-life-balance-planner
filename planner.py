from datetime import datetime, timedelta

def time_to_minutes(t):
    """Convert HH:MM string to minutes since midnight"""
    h, m = map(int, t.split(":"))
    return h * 60 + m

def generate_day_plan(tasks, slots, energy_level):
    """
    Generate a daily plan based on tasks, slots, and current energy level.

    Args:
        tasks (list of dict): Each dict has keys: name, category, duration, 
                              energy_required, priority, deadline.
        slots (list of tuple): Each tuple is (start_time_str, end_time_str) in HH:MM format.
        energy_level (str): "high", "medium", or "low"

    Returns:
        list of dict: Each dict contains scheduled task info with keys: task, slot, category
    """
    # Map energy levels to numeric for comparison
    energy_map = {"high": 3, "medium": 2, "low": 1}
    current_energy = energy_map.get(energy_level.lower(), 2)

    today = datetime.today().date()

    # Preprocess tasks
    for t in tasks:
        t["deadline"] = datetime.strptime(t["deadline"], "%Y-%m-%d").date() if t.get("deadline") else today
        t["energy_num"] = energy_map.get(t.get("energy_required", "medium").lower(), 2)
        t["is_overdue"] = t["deadline"] < today
        t["is_today"] = t["deadline"] == today

    # Separate overdue and upcoming tasks based on energy
    overdue_tasks = [t for t in tasks if t["is_overdue"] and t["energy_num"] <= current_energy]
    upcoming_tasks = [t for t in tasks if not t["is_overdue"] and t["energy_num"] <= current_energy]

    # Sort overdue: earliest missed first, then higher priority, then energy match
    overdue_tasks.sort(key=lambda t: (t["deadline"], -t["priority"], -t["energy_num"]))

    # Sort upcoming: higher priority, then energy match, then earliest deadline
    upcoming_tasks.sort(key=lambda t: (-t["priority"], -t["energy_num"], t["deadline"]))

    # Combine tasks
    sorted_tasks = overdue_tasks + upcoming_tasks

    plan = []
    slot_idx = 0

    for task in sorted_tasks:
        if slot_idx >= len(slots):
            break  # no more available slots

        remaining_duration = task["duration"]

        while remaining_duration > 0 and slot_idx < len(slots):
            start, end = slots[slot_idx]
            slot_duration = time_to_minutes(end) - time_to_minutes(start)

            # Determine allocated time for this slot
            allocate_minutes = min(remaining_duration, slot_duration)

            task_name = task["name"]
            if task["is_overdue"]:
                task_name += f" ⚠️ Overdue (Deadline: {task['deadline']})"

            # Indicate chunk if task longer than slot
            if allocate_minutes < remaining_duration:
                task_name += f" ({allocate_minutes} min chunk)"
            
            plan.append({
                "task": task_name,
                "slot": f"{start}-{end}",
                "category": task.get("category", "")
            })

            remaining_duration -= allocate_minutes
            slot_idx += 1

    return plan
