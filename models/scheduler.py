import os
import google.generativeai as genai
from dotenv import load_dotenv
import json


load_dotenv()


gemini_api_key = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=gemini_api_key)


async def analyze_request(user_message: str) -> dict:
    """Analyze if the user is requesting a study plan or just chatting"""
    prompt = f"""
    You are an AI assistant that helps users learn new subjects. Analyze the following user message:
    
    "{user_message}"
    
    Determine if the user is requesting a study plan or just chatting. Return ONLY a JSON object with this structure:
    
    {{
        "is_study_plan_request": true/false,
        "subject": "subject name if requesting a plan, otherwise null"
    }}
    
    A study plan request typically includes phrases like "I want to learn", "help me study", "create a plan", "schedule for", etc.
    
    Only return the JSON object, no explanation or additional text.
    """

    model = genai.GenerativeModel('gemini-2.0-flash')
    response = model.generate_content(prompt)
    text = response.candidates[0].content.parts[0].text

    # Clean up the response text to ensure it's valid JSON
    text = text.strip()
    if text.startswith("```json"):
        text = text[7:]
    if text.endswith("```"):
        text = text[:-3]
    text = text.strip()

    try:
        result = json.loads(text)
        return result
    except json.JSONDecodeError:
        # Default fallback if we can't parse the response
        return {"is_study_plan_request": False, "subject": None}


async def generate_chat_response(user_message: str) -> dict:
    """Generate a conversational response for general chat"""
    prompt = f"""
    You are an educational assistant AI that helps users learn new subjects. Respond to the following message conversationally:
    
    "{user_message}"
    
    Respond in a friendly, helpful manner. If the user is thanking you, acknowledge it warmly.
    If the user asks a question, answer it directly.
    If the user seems to be requesting a study plan but you're not 100% sure, suggest they can ask for a detailed study plan.
    
    Return your response as plain text, no JSON formatting.
    """

    model = genai.GenerativeModel('gemini-2.0-flash')
    response = model.generate_content(prompt)
    text = response.candidates[0].content.parts[0].text

    return {
        "type": "chat",
        "content": text.strip()
    }


async def generate_schedule(user_message: str) -> dict:
    """Generate a detailed study schedule"""
    prompt = f"""
    You are an educational assistant AI specialized in creating personalized study plans. Based on the user request: "{user_message}", generate:

    1. A short summary message that shows empathy and understanding. If the user writes in a language other than English, respond with empathy in the same language.

    2. A JSON object with a detailed study schedule for ANY subject or topic they mention. Each entry in the schedule array must include:
    * title: Specific skill, topic or concept to study (be very specific, not generic)
    * description: 2-3 sentences explaining what to study with recommended activities or resources
    * day (Monday to Sunday)
    * start and end times (HH:MM format)
    
    Output only JSON in this structure, no explanation or markdown:

    {{
    "summary": "<short message to user in their language if possible>",
    "schedule": [
        {{
            "title": "<specific topic name>",
            "description": "<detailed explanation of what to study and how>",
            "day": "Monday",
            "start": "09:00",
            "end": "10:00"
        }},
        {{
            "title": "<specific topic name>",
            "description": "<detailed explanation of what to study and how>",
            "day": "Wednesday",
            "start": "09:00",
            "end": "10:30"
        }}
    ]
    }}

    For any subject, make the schedule progressive and structured:
    - For languages: Include different skills (reading, writing, listening, speaking, vocabulary, grammar)
    - For sciences: Start with fundamental concepts before advanced topics
    - For math: Build from basic principles to more complex applications
    - For arts/music: Include both theory and practical exercises
    - For programming: Include both learning concepts and hands-on coding exercises
    - For fitness: Vary workout types and intensity throughout the week
    
    Always include:
    - Specific resources when possible (book chapters, video titles, exercise names)
    - Concrete practice activities with clear objectives
    - A logical progression that builds skills throughout the week
    - Realistic time frames for each topic
    - Mix of learning and practical application

    Only return the JSON inside a Markdown code block like this:
    ```json
    {{ ... }}
    ```
    """

    model = genai.GenerativeModel('gemini-2.0-flash')

    response = model.generate_content(prompt)
    # Extract the JSON string from the markdown code block
    text = response.candidates[0].content.parts[0].text
    json_start = text.find("```json")
    json_end = text.find("```", json_start + 1)

    if json_start == -1 or json_end == -1:
        # Fallback if markdown formatting is missing
        cleaned_text = text.strip()
        try:
            result = json.loads(cleaned_text)
        except json.JSONDecodeError:
            result = {
                "summary": "I'm sorry, I couldn't generate a proper study plan. Could you provide more details about what you want to learn?",
                "schedule": []
            }
    else:
        json_str = text[json_start + 7: json_end].strip()
        try:
            result = json.loads(json_str)
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            result = {
                "summary": "I'm sorry, I couldn't generate a proper study plan. Could you provide more details about what you want to learn?",
                "schedule": []
            }

    # Add type identifier for frontend
    return {
        "type": "study_plan",
        "content": result
    }
