import re
import json

class MusicPlanner:
    """
    Parses natural language prompts into structured musical metadata.
    Currently uses rule-based extraction (placeholder for LLM).
    """
    
    def __init__(self):
        self.genres = ["rock", "pop", "jazz", "classical", "edm", "hip hop", "rap", "metal", "country", "blues"]
        self.moods = ["happy", "sad", "energetic", "relaxed", "dark", "romantic", "angry", "uplifting"]
        
    def plan(self, prompt: str) -> dict:
        """
        Analyze the prompt and return a structured plan.
        """
        prompt_lower = prompt.lower()
        
        # Default values
        plan = {
            "original_prompt": prompt,
            "bpm": 120,
            "key": "C Major",
            "genre": "pop",
            "mood": "neutral",
            "instruments": [],
            "structure": ["Intro", "Verse", "Chorus", "Outro"],
            "description": prompt # Passed to the model
        }
        
        # Extract BPM
        bpm_match = re.search(r'(\d+)\s*bpm', prompt_lower)
        if bpm_match:
            plan["bpm"] = int(bpm_match.group(1))
            
        # Extract Genre
        for g in self.genres:
            if g in prompt_lower:
                plan["genre"] = g
                break
                
        # Extract Mood
        for m in self.moods:
            if m in prompt_lower:
                plan["mood"] = m
                break
                
        # Construct a refined description for the model
        # MusicGen works best with comma-separated tags
        tags = [plan["genre"], plan["mood"]]
        if bpm_match:
            tags.append(f"{plan['bpm']} bpm")
            
        plan["description"] = ", ".join(tags) + ", " + prompt
        
        return plan

if __name__ == "__main__":
    # Simple test
    planner = MusicPlanner()
    test_prompt = "A sad jazz song at 80 bpm about rain"
    print(json.dumps(planner.plan(test_prompt), indent=2))
