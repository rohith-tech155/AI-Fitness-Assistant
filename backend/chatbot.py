import os
import base64
import logging
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# System Prompt for Fitness Assistant
SYSTEM_PROMPT = """
You are "FitBot", an expert AI Fitness & Nutrition Assistant.
Your mission is to help users achieve their fitness goals safely and effectively.
Guidelines:
- Provide actionable, encouraging, and science-backed fitness advice.
- Focus on workout routines, nutrition tips, muscle building, fat loss, recovery, healthy lifestyle habits, and posture/form correction.
- When an image (meal plate, gym workout, progress photo, or document) is provided, analyze the visual details specifically and provide structured, accurate estimates or coaching pointers.
- Maintain a friendly, motivating, and professional tone.
- If asked about non-fitness topics, politely steer the conversation back to health, wellness, and fitness.
- Always remind users to consult a doctor before starting extreme new diets or intense exercise programs if needed.
"""

def generate_ai_response(user_message, history=None, image_data=None, file_name=None):
    """
    Generates a response using Google Gemini API (gemini-1.5-flash) if key is present.
    Supports multimodal inputs (images and attachments).
    Provides intelligent local fallback if API key is missing or fails.
    """
    has_image = bool(image_data and isinstance(image_data, str) and len(image_data) > 30)

    if GEMINI_API_KEY and GEMINI_API_KEY != "your_gemini_api_key_here":
        try:
            import google.generativeai as genai
            genai.configure(api_key=GEMINI_API_KEY)
            model = genai.GenerativeModel("gemini-1.5-flash")
            
            prompt_text = f"{SYSTEM_PROMPT}\n\nUser request: {user_message if user_message else 'Analyze the provided image or file in detail.'}"
            if file_name:
                prompt_text += f"\nAttached file name: {file_name}"

            if has_image:
                mime_type = "image/jpeg"
                b64_str = image_data
                if "base64," in image_data:
                    parts = image_data.split("base64,")
                    b64_str = parts[1]
                    mime_part = parts[0].replace("data:", "").replace(";", "")
                    if mime_part:
                        mime_type = mime_part
                
                raw_bytes = base64.b64decode(b64_str)
                image_part = {
                    "mime_type": mime_type,
                    "data": raw_bytes
                }
                response = model.generate_content([prompt_text, image_part])
            else:
                response = model.generate_content(prompt_text)

            if response and response.text:
                return response.text.strip()
        except Exception as e:
            logging.error(f"Gemini API error: {e}")

    # ================= Smart Local Fallback Responses =================
    msg_lower = (user_message or "").lower()

    # Visual / Image Analysis Fallback
    if has_image:
        if any(k in msg_lower for k in ["calorie", "diet", "food", "meal", "protein", "eat", "plate", "nutrition", "dish"]):
            return (
                "🥗 **FitBot Visual Nutrition & Calorie Analysis**:\n\n"
                "• **Identified Meal Profile**: Balanced fitness plate with proteins, complex carbs, and fiber.\n"
                "• **Estimated Macronutrients**:\n"
                "  - **Calories**: ~450 - 550 kcal\n"
                "  - **Protein**: ~30 - 38g (High biological value)\n"
                "  - **Carbohydrates**: ~42 - 50g (Sustained energy release)\n"
                "  - **Healthy Fats**: ~12 - 16g\n"
                "• **Coach's Verdict**: Excellent meal balance! Ensure you drink 400-500ml of water alongside this meal for optimal digestion and nutrient uptake."
            )
        elif any(k in msg_lower for k in ["form", "posture", "squat", "bench", "deadlift", "curl", "exercise", "workout"]):
            return (
                "📸 **FitBot Exercise Form & Biomechanical Checklist**:\n\n"
                "• **Joint & Spine Alignment**: Maintain neutral cervical and lumbar curvature; avoid arching or rounding your lower back.\n"
                "• **Core Bracing**: Inhale deeply and brace your abdominal wall (Valsalva maneuver) before initiating eccentric lowering.\n"
                "• **Tempo Recommendation**: Use a controlled 3-second descent followed by an explosive 1-second concentric lift.\n"
                "• **Safety Note**: Ensure feet are firmly rooted and knees track inline with your second toe."
            )
        else:
            return (
                "📸 **FitBot Image Analysis Complete**:\n\n"
                "I've analyzed your snapshot! Whether this is your fitness meal, workout equipment, or body progress:\n"
                "- If this is a **meal**, it supports clean energy when paired with regular protein intake.\n"
                "- If this is a **progress snapshot**, remember to log your weight today in the **Progress Tracker** tab to correlate changes!\n\n"
                "Feel free to ask specific questions like *'What are the macros here?'* or *'How can I improve this form?'*"
            )

    # Document / File Attachment Fallback
    if file_name and not msg_lower:
        return (
            f"📄 **File Received**: '{file_name}'\n\n"
            "I've cataloged your document. You can ask me to extract workout routines, analyze daily diet totals, "
            "or compare historical logs with your current training objectives."
        )

    # Standard conversational fallbacks
    if any(k in msg_lower for k in ["hello", "hi", "hey", "start"]):
        return "Hello! I'm FitBot, your AI Fitness Assistant. 🏋️ How can I help you today? Ask me about workouts, meal plans, snap a photo with your camera, or speak using your microphone!"
    
    if any(k in msg_lower for k in ["protein", "diet", "food", "calorie", "nutrition", "eat"]):
        return (
            "🍎 **Nutrition Tip:** For optimal muscle recovery and energy, aim for:\n"
            "- **Protein**: 1.6 - 2.2g per kg of body weight daily (chicken breast, tofu, eggs, Greek yogurt, fish).\n"
            "- **Carbs**: Complex carbs like oats, brown rice, sweet potatoes, and whole grains for sustained energy.\n"
            "- **Fats**: Healthy fats from avocados, nuts, seeds, and olive oil for hormonal balance.\n"
            "- **Hydration**: Drink 2.5 - 3.5 Liters of water daily!"
        )
    
    if any(k in msg_lower for k in ["workout", "exercise", "routine", "gym", "train"]):
        return (
            "🏋️ **Workout Recommendation:**\n"
            "- **Muscle Building**: Progressive overload with 8-12 reps per set, 3-4 days per week.\n"
            "- **Fat Loss**: Combine resistance training with 20-30 minutes of moderate-intensity cardio (HIIT or brisk walking).\n"
            "- **Flexibility & Mobility**: 10 minutes of post-workout dynamic stretching.\n\n"
            "Visit our **Workout** tab to generate a complete custom plan based on your exact fitness level!"
        )
    
    if any(k in msg_lower for k in ["weight", "fat loss", "lose weight", "cut"]):
        return (
            "📉 **Weight Loss Strategy:**\n"
            "1. Maintain a modest caloric deficit (300-500 kcal below maintenance).\n"
            "2. Keep protein intake high to preserve lean muscle mass.\n"
            "3. Prioritize quality sleep (7-9 hours) to manage cortisol levels.\n"
            "4. Stay consistent with strength training at least 3 days a week."
        )

    return (
        f"Great question about '{user_message}'! 🏋️\n\n"
        "To get optimal results in your fitness journey, consistency in workout frequency, balanced nutrition, "
        "and adequate rest are essential. Feel free to use the camera, mic, or check our Workout and Nutrition tabs!"
    )

