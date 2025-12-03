import os

def summarize_medical_history(raw_history):
    """Summarize medical history using Gemini AI"""
    if not raw_history or not raw_history.strip():
        return "No medical history provided."
    
    api_key = os.environ.get("GEMINI_API_KEY")
    
    if not api_key:
        return "AI summary unavailable - API key not configured. Raw history preserved."
    
    try:
        from google import genai
        
        client = genai.Client(api_key=api_key)
        
        prompt = f"Summarize this medical history into 3 bullet points:\n\n{raw_history}"
        
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        
        return response.text if response.text else "Unable to generate summary."
        
    except Exception as e:
        return f"AI summary unavailable: {str(e)}"
