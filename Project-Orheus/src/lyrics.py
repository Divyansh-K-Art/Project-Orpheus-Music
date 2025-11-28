import re
from typing import List, Dict, Tuple

class LyricGenerator:
    """
    Generates and formats lyrics for music generation.
    Currently template-based; will be replaced with LLM in Phase 2.
    """
    
    def __init__(self):
        self.templates = {
            "happy": {
                "verse": [
                    "Dancing through the day",
                    "Sunshine lights the way",
                    "Feeling so alive",
                    "Good vibes never die"
                ],
                "chorus": [
                    "We're flying high tonight",
                    "Everything feels right",
                    "Hearts are shining bright",
                    "Living in the light"
                ]
            },
            "sad": {
                "verse": [
                    "Walking in the rain",
                    "Feeling all the pain",
                    "Memories remain",
                    "Nothing stays the same"
                ],
                "chorus": [
                    "Missing you tonight",
                    "Fading from my sight",
                    "Lost without your light",
                    "Can't make this right"
                ]
            },
            "energetic": {
                "verse": [
                    "Feel the rhythm rise",
                    "Fire in our eyes",
                    "Ready for the night",
                    "Gonna reach new heights"
                ],
                "chorus": [
                    "Turn it up, let's go",
                    "Feel the energy flow",
                    "We're unstoppable",
                    "Watch us steal the show"
                ]
            }
        }
    
    def generate(self, mood: str, structure: List[str]) -> Dict[str, List[str]]:
        """
        Generate lyrics based on mood and song structure.
        
        Returns:
            Dict mapping section name to list of lyric lines
        """
        mood = mood.lower()
        if mood not in self.templates:
            mood = "happy"  # Default fallback
            
        template = self.templates[mood]
        lyrics = {}
        
        for section in structure:
            section_lower = section.lower()
            if "verse" in section_lower:
                lyrics[section] = template["verse"]
            elif "chorus" in section_lower:
                lyrics[section] = template["chorus"]
            else:
                # Intro/Outro typically instrumental
                lyrics[section] = ["[Instrumental]"]
                
        return lyrics
    
    def format_for_musicgen(self, lyrics_dict: Dict[str, List[str]]) -> str:
        """
        Format lyrics into a single string suitable for MusicGen conditioning.
        """
        all_lines = []
        for section, lines in lyrics_dict.items():
            if lines != ["[Instrumental]"]:
                all_lines.extend(lines)
        
        return " / ".join(all_lines)


class LyricAligner:
    """
    Simulates phoneme-level alignment for future implementation.
    In production, this would use Montreal Forced Aligner or similar.
    """
    
    def __init__(self):
        pass
    
    def estimate_timings(self, lyrics: str, duration_sec: float, bpm: int) -> List[Tuple[float, float, str]]:
        """
        Estimate rough timing for each word in lyrics.
        
        Args:
            lyrics: Full lyric text
            duration_sec: Total song duration in seconds
            bpm: Beats per minute
            
        Returns:
            List of (start_time, end_time, word) tuples
        """
        words = lyrics.split()
        if not words:
            return []
        
        # Simple uniform distribution
        # In reality, this would use phoneme duration models
        time_per_word = duration_sec / len(words)
        
        timings = []
        current_time = 0.0
        
        for word in words:
            start = current_time
            end = current_time + time_per_word
            timings.append((start, end, word))
            current_time = end
            
        return timings
    
    def generate_alignment_prompt(self, lyrics: str, structure: List[str]) -> str:
        """
        Generate a conditioning string that includes structure hints.
        Format: [SECTION_NAME] lyrics [SECTION_NAME] ...
        """
        # This is a placeholder for a more sophisticated approach
        # In practice, we'd interleave section markers with lyrics
        return f"[Song with structure: {', '.join(structure)}] {lyrics}"


if __name__ == "__main__":
    # Test the lyric generator
    generator = LyricGenerator()
    aligner = LyricAligner()
    
    structure = ["Intro", "Verse", "Chorus", "Verse", "Chorus", "Outro"]
    lyrics = generator.generate("sad", structure)
    
    print("Generated Lyrics:")
    print("=" * 50)
    for section, lines in lyrics.items():
        print(f"\n[{section}]")
        for line in lines:
            print(f"  {line}")
    
    print("\n" + "=" * 50)
    formatted = generator.format_for_musicgen(lyrics)
    print(f"\nFormatted for MusicGen:\n{formatted}")
    
    print("\n" + "=" * 50)
    timings = aligner.estimate_timings(formatted, duration_sec=30, bpm=80)
    print(f"\nEstimated Word Timings (first 5):")
    for start, end, word in timings[:5]:
        print(f"  {start:.2f}s - {end:.2f}s: {word}")
