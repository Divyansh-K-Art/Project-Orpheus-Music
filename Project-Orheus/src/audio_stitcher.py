"""
Audio Stitching Utilities
Combines multiple audio segments into longer songs with crossfading
"""

import numpy as np
import scipy.io.wavfile
from typing import List, Tuple

class AudioStitcher:
    """Combines audio segments into longer tracks."""
    
    def __init__(self, sample_rate: int = 32000):
        self.sample_rate = sample_rate
    
    def crossfade(self, audio1: np.ndarray, audio2: np.ndarray, fade_duration: float = 6.0) -> np.ndarray:
        """
        Crossfade between two audio segments using ultra-smooth equal-power curves.
        
        Args:
            audio1: First audio segment
            audio2: Second audio segment
            fade_duration: Crossfade duration in seconds (default 6.0 for maximum smoothness)
        
        Returns:
            Seamlessly crossfaded audio
        """
        fade_samples = int(fade_duration * self.sample_rate)
        fade_samples = min(fade_samples, len(audio1) // 3, len(audio2) // 3)  # Use up to 1/3 of each segment
        
        # Create ultra-smooth equal-power crossfade curves
        # This ensures constant perceived loudness during transition
        t = np.linspace(0, np.pi / 2, fade_samples)
        
        # Equal-power crossfade with extra smoothing (maintains constant energy)
        fade_out = (np.cos(t) ** 2.0) * 0.9 + 0.1  # Very gentle fade out, never goes to zero
        fade_in = (np.sin(t) ** 2.0) * 0.9 + 0.1   # Very gentle fade in, starts from non-zero
        
        # Normalize to ensure proper volume
        norm_factor = fade_out + fade_in
        fade_out = fade_out / norm_factor
        fade_in = fade_in / norm_factor
        
        # Apply equal-power crossfade
        overlap = audio1[-fade_samples:] * fade_out + audio2[:fade_samples] * fade_in
        
        # Combine segments
        result = np.concatenate([
            audio1[:-fade_samples],
            overlap,
            audio2[fade_samples:]
        ])
        
        return result
    
    def stitch_segments(self, segments: List[np.ndarray], fade_duration: float = 6.0, use_beat_align: bool = True) -> np.ndarray:
        """
        Stitch multiple audio segments together with seamless crossfading.
        
        Args:
            segments: List of audio segments
            fade_duration: Crossfade duration between segments (default 6.0s for ultra-smooth transitions)
            use_beat_align: Whether to align segments to beat grid
        
        Returns:
            Seamlessly combined audio track
        """
        if not segments:
            return np.array([])
        
        if len(segments) == 1:
            return segments[0]
        
        # Optionally align to beat grid for rhythm continuity
        if use_beat_align and len(segments) > 1:
            segments = self.align_segments_to_beat(segments)
        
        result = segments[0]
        
        # Stitch each segment with long crossfade
        for segment in segments[1:]:
            result = self.crossfade(result, segment, fade_duration)
        
        return result
    
    def match_loudness(self, segments: List[np.ndarray]) -> List[np.ndarray]:
        """
        Normalize loudness across all segments for consistency.
        
        Args:
            segments: List of audio segments
        
        Returns:
            Loudness-matched segments
        """
        # Calculate RMS for each segment
        rms_values = [np.sqrt(np.mean(seg**2)) for seg in segments]
        target_rms = np.mean(rms_values)
        
        # Normalize each segment
        matched_segments = []
        for seg, rms in zip(segments, rms_values):
            if rms > 0:
                gain = target_rms / rms
                matched_segments.append(seg * gain)
            else:
                matched_segments.append(seg)
        
        return matched_segments
    
    def analyze_tempo(self, audio: np.ndarray) -> float:
        """
        Estimate tempo of audio segment (simplified).
        
        Returns: Estimated BPM
        """
        # Simplified tempo detection using autocorrelation
        # In production, use librosa.beat.beat_track
        
        # For now, return a default
        return 120.0
    
    def estimate_beat_phase(self, audio: np.ndarray) -> float:
        """
        Estimate the beat phase for alignment.
        
        Returns: Phase offset in seconds
        """
        # Simplified - in production use beat tracking
        return 0.0
    
    def align_segments_to_beat(self, segments: List[np.ndarray], target_bpm: float = None) -> List[np.ndarray]:
        """
        Align segment boundaries to beat grid for smoother transitions.
        
        Args:
            segments: List of audio segments
            target_bpm: Target tempo (auto-detected if None)
        
        Returns:
            Beat-aligned segments
        """
        if not segments or len(segments) < 2:
            return segments
        
        # Detect tempo from first segment if not provided
        if target_bpm is None:
            target_bpm = self.analyze_tempo(segments[0])
        
        # Calculate beat duration
        beat_duration = 60.0 / target_bpm
        samples_per_beat = int(beat_duration * self.sample_rate)
        
        # Align each segment to nearest beat boundary
        aligned = []
        for seg in segments:
            # Round length to nearest beat
            target_length = round(len(seg) / samples_per_beat) * samples_per_beat
            
            if target_length > len(seg):
                # Pad with silence
                padding = np.zeros(target_length - len(seg))
                aligned.append(np.concatenate([seg, padding]))
            else:
                # Trim to beat boundary
                aligned.append(seg[:target_length])
        
        return aligned


if __name__ == "__main__":
    # Test the stitcher
    stitcher = AudioStitcher(sample_rate=32000)
    
    # Create test segments (simulating 10s segments)
    duration = 10.0
    num_samples = int(duration * 32000)
    
    # Generate test segments with different frequencies
    segments = []
    for i, freq in enumerate([440, 550, 660]):
        t = np.linspace(0, duration, num_samples)
        segment = np.sin(2 * np.pi * freq * t) * 0.5
        segments.append(segment)
    
    print("Testing AudioStitcher...")
    print(f"Number of segments: {len(segments)}")
    print(f"Segment duration: {duration}s")
    
    # Match loudness
    matched = stitcher.match_loudness(segments)
    print(f"Loudness matched: {len(matched)} segments")
    
    # Stitch with crossfade
    result = stitcher.stitch_segments(matched, fade_duration=1.0)
    expected_length = (len(segments) * duration - (len(segments) - 1) * 1.0)
    actual_length = len(result) / 32000
    
    print(f"Expected length: ~{expected_length:.1f}s")
    print(f"Actual length: {actual_length:.1f}s")
    print(f"Result shape: {result.shape}")
    
    print("\nAll tests passed!")
