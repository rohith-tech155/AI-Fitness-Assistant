import os
import json
import logging
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

def generate_workout_routine(goal, level, equipment="General Gym Equipment"):
    """
    Generates a structured workout routine based on goal and fitness level.
    """
    if GEMINI_API_KEY and GEMINI_API_KEY != "your_gemini_api_key_here":
        try:
            import google.generativeai as genai
            genai.configure(api_key=GEMINI_API_KEY)
            model = genai.GenerativeModel("gemini-1.5-flash")
            
            prompt = f"""
            Create a structured 4-day workout plan for a user with the following profile:
            - Goal: {goal}
            - Fitness Level: {level}
            - Equipment Available: {equipment}

            Format your response strictly as a valid JSON object with the following structure:
            {{
                "title": "Workout Plan Name",
                "overview": "Brief description of the plan",
                "days": [
                    {{
                        "day": "Day 1: Muscle Target",
                        "exercises": [
                            {{"name": "Exercise Name", "sets": "3", "reps": "10-12", "rest": "60 sec"}}
                        ]
                    }}
                ],
                "tips": ["Tip 1", "Tip 2"]
            }}
            Return ONLY the raw JSON string without markdown formatting or code blocks.
            """
            
            response = model.generate_content(prompt)
            if response and response.text:
                clean_text = response.text.replace("```json", "").replace("```", "").strip()
                parsed = json.loads(clean_text)
                return parsed
        except Exception as e:
            logging.error(f"Gemini AI Workout generation error: {e}")

    # Template Fallbacks by Goal & Level
    return generate_fallback_workout(goal, level)

def generate_fallback_workout(goal, level):
    """Generates comprehensive structured workout templates."""
    goal_key = goal.lower()
    level_key = level.lower()
    
    if "muscle" in goal_key or "strength" in goal_key:
        return {
            "title": f"Hypertrophy Muscle Builder ({level.capitalize()})",
            "overview": f"Designed for maximum muscle growth and strength progression tailored for {level} lifters.",
            "days": [
                {
                    "day": "Day 1: Upper Body (Chest & Back focus)",
                    "exercises": [
                        {"name": "Barbell / Dumbbell Bench Press", "sets": "4", "reps": "8 - 10", "rest": "90 sec"},
                        {"name": "Bent-Over Rows or Lat Pulldowns", "sets": "4", "reps": "8 - 12", "rest": "90 sec"},
                        {"name": "Incline Dumbbell Press", "sets": "3", "reps": "10 - 12", "rest": "60 sec"},
                        {"name": "Cable Rows or Overhead Press", "sets": "3", "reps": "10 - 12", "rest": "60 sec"},
                        {"name": "Bicep Curls & Tricep Pushdowns", "sets": "3", "reps": "12 - 15", "rest": "45 sec"}
                    ]
                },
                {
                    "day": "Day 2: Lower Body & Core",
                    "exercises": [
                        {"name": "Barbell Squats or Leg Press", "sets": "4", "reps": "8 - 10", "rest": "90-120 sec"},
                        {"name": "Romanian Deadlifts", "sets": "3", "reps": "8 - 10", "rest": "90 sec"},
                        {"name": "Walking Lunges", "sets": "3", "reps": "12 per leg", "rest": "60 sec"},
                        {"name": "Standing Calf Raises", "sets": "4", "reps": "15", "rest": "45 sec"},
                        {"name": "Hanging Leg Raises / Planks", "sets": "3", "reps": "15-20 / 60 sec", "rest": "45 sec"}
                    ]
                },
                {
                    "day": "Day 3: Rest & Active Recovery",
                    "exercises": [
                        {"name": "Light Walking or Cycling", "sets": "1", "reps": "30 mins", "rest": "N/A"},
                        {"name": "Full Body Mobility & Foam Rolling", "sets": "1", "reps": "15 mins", "rest": "N/A"}
                    ]
                },
                {
                    "day": "Day 4: Shoulders & Arms Blitz",
                    "exercises": [
                        {"name": "Overhead Dumbbell Press", "sets": "4", "reps": "8 - 10", "rest": "90 sec"},
                        {"name": "Lateral Dumbbell Raises", "sets": "4", "reps": "12 - 15", "rest": "45 sec"},
                        {"name": "Face Pulls", "sets": "3", "reps": "15", "rest": "45 sec"},
                        {"name": "Barbell Bicep Curls", "sets": "3", "reps": "10 - 12", "rest": "60 sec"},
                        {"name": "Skullcrushers / Dips", "sets": "3", "reps": "10 - 12", "rest": "60 sec"}
                    ]
                }
            ],
            "tips": [
                "Increase weight slightly when you can hit upper rep range with clean form.",
                "Ensure at least 1.8g of protein per kg of body weight for muscle repair.",
                "Prioritize 7-9 hours of restful sleep every night."
            ]
        }
    
    elif "fat" in goal_key or "loss" in goal_key or "weight" in goal_key:
        return {
            "title": f"Metabolic Fat Burner ({level.capitalize()})",
            "overview": f"High-density circuit routine to maximize calorie burn and preserve lean muscle mass for {level} users.",
            "days": [
                {
                    "day": "Day 1: Full Body HIIT & Strength",
                    "exercises": [
                        {"name": "Goblet Squats", "sets": "4", "reps": "12 - 15", "rest": "45 sec"},
                        {"name": "Push-Ups (or Kneeling Push-ups)", "sets": "4", "reps": "12 - 15", "rest": "45 sec"},
                        {"name": "Kettlebell / Dumbbell Swings", "sets": "4", "reps": "15 - 20", "rest": "45 sec"},
                        {"name": "Mountain Climbers", "sets": "3", "reps": "45 sec", "rest": "30 sec"},
                        {"name": "Treadmill Interval Sprints", "sets": "8 rounds", "reps": "30 sec sprint / 60 sec walk", "rest": "N/A"}
                    ]
                },
                {
                    "day": "Day 2: Cardio & Core Conditioning",
                    "exercises": [
                        {"name": "Rowing Machine or Cycling", "sets": "1", "reps": "25 mins moderate", "rest": "N/A"},
                        {"name": "Plank to Push-up", "sets": "3", "reps": "10 reps", "rest": "45 sec"},
                        {"name": "Russian Twists", "sets": "3", "reps": "20 total", "rest": "30 sec"},
                        {"name": "Bicycle Crunches", "sets": "3", "reps": "20 total", "rest": "30 sec"}
                    ]
                },
                {
                    "day": "Day 3: Lower Body & Plyometrics",
                    "exercises": [
                        {"name": "Dumbbell Deadlifts", "sets": "4", "reps": "12", "rest": "60 sec"},
                        {"name": "Jump Squats / Air Squats", "sets": "4", "reps": "15", "rest": "45 sec"},
                        {"name": "Reverse Lunges", "sets": "3", "reps": "12 per leg", "rest": "45 sec"},
                        {"name": "Box Jumps or Step-ups", "sets": "3", "reps": "10 - 12", "rest": "45 sec"}
                    ]
                }
            ],
            "tips": [
                "Combine this routine with a 300-500 kcal daily deficit.",
                "Drink water before, during, and after your workouts.",
                "Keep rest periods brisk to keep your heart rate elevated."
            ]
        }
    else:
        # Default General Fitness / Endurance
        return {
            "title": f"Balanced Vitality & Fitness Plan ({level.capitalize()})",
            "overview": f"A balanced split covering cardiovascular health, total body strength, and mobility for {level} level.",
            "days": [
                {
                    "day": "Day 1: Total Body Strength",
                    "exercises": [
                        {"name": "Dumbbell Squats", "sets": "3", "reps": "10 - 12", "rest": "60 sec"},
                        {"name": "Dumbbell Chest Press", "sets": "3", "reps": "10 - 12", "rest": "60 sec"},
                        {"name": "Lat Pulldown or Inverted Rows", "sets": "3", "reps": "10 - 12", "rest": "60 sec"},
                        {"name": "Plank Hold", "sets": "3", "reps": "45 - 60 sec", "rest": "45 sec"}
                    ]
                },
                {
                    "day": "Day 2: Cardio & Endurance",
                    "exercises": [
                        {"name": "Brisk Jogging / Cycling", "sets": "1", "reps": "30 mins continuous", "rest": "N/A"},
                        {"name": "Jumping Jacks & Burpees", "sets": "3", "reps": "10 reps each", "rest": "45 sec"}
                    ]
                },
                {
                    "day": "Day 3: Active Mobility & Core",
                    "exercises": [
                        {"name": "Bodyweight Squats", "sets": "3", "reps": "15", "rest": "45 sec"},
                        {"name": "Bird-Dogs & Cat-Cows", "sets": "3", "reps": "12 per side", "rest": "30 sec"},
                        {"name": "Hamstring & Hip Flexor Stretches", "sets": "1", "reps": "15 mins", "rest": "N/A"}
                    ]
                }
            ],
            "tips": [
                "Focus on smooth technique before increasing weight.",
                "Stay active with daily walking ( aim for 8,000-10,000 steps).",
                "Ensure proper warm-up prior to each exercise session."
            ]
        }
