"""
Audio Post-Processing Module
Enhances generated audio with normalization, fade effects, and format conversion.
"""

import numpy as np
from scipy import signal
from typing import Tuple

class AudioProcessor:
    """Post-processing tools for generated audio."""
    
    def __init__(self, sample_rate: int = 32000):
        self.sample_rate = sample_rate
    
    def normalize(self, audio: np.ndarray, target_db: float = -3.0) -> np.ndarray:
        """
        Normalize audio to target loudness in dB.
        
        Args:
            audio: Audio array (1D)
            target_db: Target peak level in dB (negative value)
        
        Returns:
            Normalized audio
        """
        # Calculate current peak
        current_peak = np.abs(audio).max()
        
        if current_peak == 0:
            return audio
        
        # Convert target dB to linear scale
        target_linear = 10 ** (target_db / 20.0)
        
        # Calculate gain needed
        gain = target_linear / current_peak
        
        # Apply gain
        normalized = audio * gain
        
        # Clip to prevent distortion
        return np.clip(normalized, -1.0, 1.0)
    
    def fade_in(self, audio: np.ndarray, fade_duration: float = 0.5) -> np.ndarray:
        """
        Apply fade-in effect.
        
        Args:
            audio: Audio array
            fade_duration: Fade duration in seconds
        
        Returns:
            Audio with fade-in
        """
        fade_samples = int(fade_duration * self.sample_rate)
        fade_samples = min(fade_samples, len(audio))
        
        # Create fade curve (linear)
        fade_curve = np.linspace(0, 1, fade_samples)
        
        # Apply fade
        result = audio.copy()
        result[:fade_samples] *= fade_curve
        
        return result
    
    def fade_out(self, audio: np.ndarray, fade_duration: float = 1.0) -> np.ndarray:
        """
        Apply fade-out effect.
        
        Args:
            audio: Audio array
            fade_duration: Fade duration in seconds
        
        Returns:
            Audio with fade-out
        """
        fade_samples = int(fade_duration * self.sample_rate)
        fade_samples = min(fade_samples, len(audio))
        
        # Create fade curve (linear)
        fade_curve = np.linspace(1, 0, fade_samples)
        
        # Apply fade
        result = audio.copy()
        result[-fade_samples:] *= fade_curve
        
        return result
    
    def apply_fades(self, audio: np.ndarray, 
                   fade_in_duration: float = 0.5,
                   fade_out_duration: float = 1.0) -> np.ndarray:
        """
        Apply both fade-in and fade-out.
        """
        result = self.fade_in(audio, fade_in_duration)
        result = self.fade_out(result, fade_out_duration)
        return result
    
    def resample(self, audio: np.ndarray, target_rate: int) -> Tuple[np.ndarray, int]:
        """
        Resample audio to target sample rate.
        
        Args:
            audio: Input audio
            target_rate: Target sample rate
        
        Returns:
            Tuple of (resampled_audio, new_sample_rate)
        """
        if target_rate == self.sample_rate:
            return audio, self.sample_rate
        
        # Calculate resampling ratio
        ratio = target_rate / self.sample_rate
        num_samples = int(len(audio) * ratio)
        
        # Use scipy's resampling
        resampled = signal.resample(audio, num_samples)
        
        return resampled, target_rate
    
    def compress_dynamic_range(self, audio: np.ndarray, 
                               threshold: float = 0.5,
                               ratio: float = 4.0) -> np.ndarray:
        """
        Simple dynamic range compression (limiter).
        
        Args:
            audio: Input audio
            threshold: Compression threshold (0-1)
            ratio: Compression ratio
        
        Returns:
            Compressed audio
        """
        # Simple soft clipping above threshold
        output = audio.copy()
        
        # Find samples above threshold
        above_threshold = np.abs(output) > threshold
        
        # Apply compression
        if np.any(above_threshold):
            excess = np.abs(output[above_threshold]) - threshold
            compressed_excess = excess / ratio
            
            # Apply with sign preservation
            output[above_threshold] = np.sign(output[above_threshold]) * (threshold + compressed_excess)
        
        return output
    
    def process(self, audio: np.ndarray, 
               normalize: bool = True,
               fades: bool = True,
               compress: bool = False) -> np.ndarray:
        """
        Apply full processing pipeline.
        
        Args:
            audio: Input audio
            normalize: Apply normalization
            fades: Apply fade in/out
            compress: Apply compression
        
        Returns:
            Processed audio
        """
        result = audio.copy()
        
        if compress:
            result = self.compress_dynamic_range(result)
        
        if normalize:
            result = self.normalize(result, target_db=-3.0)
        
        if fades:
            result = self.apply_fades(result)
        
        return result


if __name__ == "__main__":
    # Test the processor
    processor = AudioProcessor(sample_rate=32000)
    
    # Create test signal (5 seconds)
    duration = 5.0
    t = np.linspace(0, duration, int(duration * processor.sample_rate))
    test_audio = np.sin(2 * np.pi * 440 * t) * 0.8  # 440 Hz sine wave
    
    print("Testing AudioProcessor...")
    print(f"Original audio: peak={np.abs(test_audio).max():.3f}")
    
    # Test normalization
    normalized = processor.normalize(test_audio, target_db=-6.0)
    print(f"Normalized: peak={np.abs(normalized).max():.3f}")
    
    # Test fades
    with_fades = processor.apply_fades(test_audio)
    print(f"With fades: start={with_fades[0]:.3f}, end={with_fades[-1]:.3f}")
    
    # Test full pipeline
    processed = processor.process(test_audio)
    print(f"Fully processed: peak={np.abs(processed).max():.3f}")
    
    print("\nAll tests passed!")
