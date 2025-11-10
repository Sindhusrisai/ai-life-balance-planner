# advisor.py

def generate_advice(user_info, plan, energy_level):
    """
    Return a simple placeholder advice instead of calling any external API.
    """
    if not plan:
        return "No tasks scheduled, so no advice available."
    
    # Example advice based on energy level
    advice_map = {
        "high": "You have high energy! Focus on the most challenging tasks first. 💪",
        "medium": "Maintain steady progress and take short breaks. ✅",
        "low": "Focus on small, easy tasks and recharge your energy. ☕"
    }
    
    return advice_map.get(energy_level.lower(), "Stay focused and take breaks between tasks. You got this! 💪")
