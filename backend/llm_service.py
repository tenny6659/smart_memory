import httpx
import os
import json
import re
from dotenv import load_dotenv

load_dotenv()

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3:latest"

def _sanitize_json(text: str) -> str:
    """
    Remove markdown code blocks and extra text to extract clean JSON.
    """
    # 1. Strip markdown code fences
    text = re.sub(r'```(?:json)?\s*|\s*```', '', text, flags=re.IGNORECASE).strip()
    
    # 2. Find the first '{' and the last '}'
    first_brace = text.find('{')
    last_brace = text.rfind('}')
    
    if first_brace != -1 and last_brace != -1:
        return text[first_brace:last_brace+1]
    return text

def _ollama_generate(prompt: str, format_json: bool = False) -> str:
    """
    Call local Ollama API for generation.
    """
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False
    }
    if format_json:
        payload["format"] = "json"
        
    try:
        response = httpx.post(OLLAMA_URL, json=payload, timeout=30.0)
        response.raise_for_status()
        res_json = response.json()
        print(f"DEBUG: Ollama response: {res_json.get('response', '')[:100]}...")
        return res_json.get("response", "")
    except Exception as e:
        print(f"DEBUG: Ollama call failed. Error: {e}")
        return ""

def classify_input(prompt_text: str):
    """
    Classify input as saved or skipped for memory.
    """
    prompt = f"""
    Task: Classify if the user is sharing a personal fact or just making small talk.
    Rules:
    - "saved": User shares names, family, job, location, likes, or skills.
    - "skipped": User says hello, hi, asks general knowledge, or small talk.
    
    Input: "{prompt_text}"
    
    Return JSON format: {{"decision": "saved"|"skipped", "category": "Personal Identity"|"Work & Learning"|"Interests & Lifestyle", "importance": 0.8}}
    """
    
    response_text = _ollama_generate(prompt, format_json=True)
    try:
        return json.loads(_sanitize_json(response_text))
    except:
        return {"decision": "skipped", "category": "General", "importance": 0.0}

def extract_entities_and_relations(text: str):
    """
    Extract graph data from personal facts.
    """
    prompt = f"""
    Extract entities and relations from: "{text}"
    Rules:
    - Always include 'User' as PERSON.
    - Entities: PERSON, COMPANY, LOCATION, SKILL, INTEREST.
    - Relations: WORKS_AT, LIVES_IN, HAS_SKILL, LIKES, KNOWS.
    
    Return JSON format: {{"entities": [{{"name": "...", "type": "..."}}], "relations": [{{"source": "User", "target": "...", "type": "..."}}]}}
    """
    
    response_text = _ollama_generate(prompt, format_json=True)
    try:
        return json.loads(_sanitize_json(response_text))
    except:
        return {"entities": [], "relations": []}

def generate_chat_response(prompt: str, context_memories: list):
    """
    Generate a natural response using retrieved memories.
    """
    # Relevance check: only include memories with distance < 0.4
    relevant_memories = [m for m in context_memories if m.get("distance", 1.0) < 0.4]
    
    context_str = ""
    if relevant_memories:
        context_str = "Personal facts you know about the user:\n" + "\n".join([f"- {m['text']}" for m in relevant_memories])

    system_instr = f"""
    You are a helpful personal assistant.
    Instructions:
    - Respond naturally in 1-2 sentences.
    - Use relevant personal facts only if they fit the context.
    - Never mention your memory system.
    
    {context_str}
    
    User: {prompt}
    Assistant:"""
    
    response_text = _ollama_generate(system_instr)
    return response_text.strip()

def merge_memories_llm(existing_text: str, new_text: str):
    """
    Combine two similar memories into one.
    """
    prompt = f"""
    Combine these two pieces of information into one concise statement:
    1. {existing_text}
    2. {new_text}
    
    Return only the combined sentence.
    """
    
    return _ollama_generate(prompt).strip()
