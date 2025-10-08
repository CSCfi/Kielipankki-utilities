#!/usr/bin/env python3
"""
An ASR script with multi-format audio support, segmentation, and Whisper-style output formatting.
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import List, Tuple, Dict, Optional
import warnings

try:
    import torch
    import librosa
    import numpy as np
    from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC
except ImportError:
    print("Error: Missing required dependencies!")
    print("This script needs to be executed within the container environment.")
    print("Please run: apptainer exec samiasr.sif python samiasr.py [args]")
    sys.exit(1)


models_path = os.environ.get("MODELS_PATH", "/opt/models")
model_name = "getman-wav2vec-large-sami"
sami_model_path = Path(models_path) / model_name
os.environ["HF_HOME"] = "/tmp/hfcache"

# Default values for command-line arguments and configuration
DEFAULT_SILENCE_THRESHOLD = 0.025
DEFAULT_MIN_SILENCE_DURATION = 0.25
DEFAULT_MIN_SEGMENT_DURATION = 3.0
DEFAULT_MAX_SEGMENT_DURATION = 60.0

# Global timing variables for profiling
model_loading_duration = 0.0
audio_loading_duration = 0.0
silence_detection_duration = 0.0
segmentation_duration = 0.0
inference_duration = 0.0


def main():
    # Suppress warnings for cleaner output
    warnings.filterwarnings("ignore", category=UserWarning)
    warnings.filterwarnings("ignore", category=FutureWarning)

    if not sami_model_path.exists():
        print(f"Error: Model not found at {sami_model_path}")
        print("This script needs to be executed within the container environment.")
        print("Please run: apptainer exec samiasr.sif python samiasr.py [args]")
        sys.exit(1)

    parser = argparse.ArgumentParser(
        description="Automatic Speech Recognition for Sámi Languages",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s audio.wav                   # Transcribe with segmentation
  %(prog)s audio.mp3 --no-segment      # Transcribe without segmentation
  %(prog)s audio.flac --json out.json  # Output to JSON file
  %(prog)s audio.wav -v                # Verbose output
        """,
    )

    parser.add_argument("input_file", help="Path to the audio file to transcribe")

    parser.add_argument(
        "--no-segment",
        action="store_true",
        help="Disable audio segmentation (process entire file as one segment)",
    )

    parser.add_argument(
        "--json", metavar="FILE", help="Output transcription to JSON file"
    )

    parser.add_argument(
        "--silence-threshold",
        type=float,
        default=DEFAULT_SILENCE_THRESHOLD,
        help=f"RMS threshold for silence detection (default: {DEFAULT_SILENCE_THRESHOLD})",
    )

    parser.add_argument(
        "--min-silence",
        type=float,
        default=DEFAULT_MIN_SILENCE_DURATION,
        help=f"Minimum silence duration in seconds (default: {DEFAULT_MIN_SILENCE_DURATION})",
    )

    parser.add_argument(
        "--min-segment",
        type=float,
        default=DEFAULT_MIN_SEGMENT_DURATION,
        help=f"Minimum segment duration in seconds (default: {DEFAULT_MIN_SEGMENT_DURATION})",
    )

    parser.add_argument(
        "--max-segment",
        type=float,
        default=DEFAULT_MAX_SEGMENT_DURATION,
        help=f"Maximum segment duration in seconds (default: {DEFAULT_MAX_SEGMENT_DURATION})",
    )

    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose output"
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug output with timing information",
    )

    args = parser.parse_args()

    # Validate input file
    if not os.path.exists(args.input_file):
        print(f"Error: Input file '{args.input_file}' does not exist.")
        sys.exit(1)

    # Create configuration
    config = SamiASRConfig()
    config.silence_threshold = args.silence_threshold
    config.min_silence_duration = args.min_silence
    config.min_segment_duration = args.min_segment
    config.max_segment_duration = args.max_segment

    try:
        # Initialize ASR processor
        if args.debug:
            print("Starting model loading...")
        model_start_time = time.time()
        asr = SamiASR(config, verbose=args.verbose)
        global model_loading_duration
        model_loading_duration = time.time() - model_start_time

        # Process the file
        start_time = time.time()
        segments = asr.process_file(args.input_file, args.no_segment)
        processing_time = time.time() - start_time

        # Output results
        if args.json:
            output_json(segments, args.json)
            if args.verbose:
                print(f"JSON output written to: {args.json}")
        else:
            print_whisper_style(segments)

        if args.debug:
            total_duration = sum(segment.duration() for segment in segments)
            total_profiled_time = (
                model_loading_duration
                + audio_loading_duration
                + silence_detection_duration
                + segmentation_duration
                + inference_duration
            )

            print(f"\n{'='*60}")
            print("DEBUG: Performance Profiling")
            print(f"{'='*60}")
            print(f"{'Device':<25}: {asr.device_name}")
            print(f"{'PyTorch CUDA available':<25}: {torch.cuda.is_available()}")
            print(f"{'Model device':<25}: {next(asr.model.parameters()).device}")

            # Additional CUDA diagnostics
            print(f"{'PyTorch version':<25}: {torch.__version__}")
            if torch.cuda.is_available():
                print(f"{'CUDA version':<25}: {torch.version.cuda}")
                print(f"{'CUDA device count':<25}: {torch.cuda.device_count()}")
            else:
                print("CUDA DIAGNOSTICS:")
                print(f"  torch.cuda.is_available(): {torch.cuda.is_available()}")
                print(
                    f"  CUDA_VISIBLE_DEVICES: {os.environ.get('CUDA_VISIBLE_DEVICES', 'Not set')}"
                )
                print(
                    f"  LD_LIBRARY_PATH: {os.environ.get('LD_LIBRARY_PATH', 'Not set')[:100]}..."
                )
                try:
                    import subprocess

                    result = subprocess.run(
                        ["nvidia-smi"], capture_output=True, text=True, timeout=5
                    )
                    if result.returncode == 0:
                        print(f"  nvidia-smi: Available")
                    else:
                        print(f"  nvidia-smi: Failed (return code {result.returncode})")
                except:
                    print(f"  nvidia-smi: Not found or failed")

            print(f"{'-'*60}")
            print(
                f"{'Model loading':<25}: {model_loading_duration:8.4f}s ({model_loading_duration/total_profiled_time*100:5.1f}%)"
            )
            print(
                f"{'Audio loading':<25}: {audio_loading_duration:8.4f}s ({audio_loading_duration/total_profiled_time*100:5.1f}%)"
            )
            print(
                f"{'Silence detection':<25}: {silence_detection_duration:8.4f}s ({silence_detection_duration/total_profiled_time*100:5.1f}%)"
            )
            print(
                f"{'Segmentation':<25}: {segmentation_duration:8.4f}s ({segmentation_duration/total_profiled_time*100:5.1f}%)"
            )
            print(
                f"{'Inference':<25}: {inference_duration:8.4f}s ({inference_duration/total_profiled_time*100:5.1f}%)"
            )
            print(f"{'-'*60}")
            print(f"{'Total profiled time':<25}: {total_profiled_time:8.4f}s")
            print(f"{'Total processing time':<25}: {processing_time:8.4f}s")
            print(f"{'Audio duration':<25}: {total_duration:8.4f}s")
            print(f"{'Real-time factor':<25}: {processing_time/total_duration:8.4f}x")
            print(f"{'Segments processed':<25}: {len(segments)}")
            print(f"{'='*60}")

        if args.verbose:
            total_duration = sum(segment.duration() for segment in segments)
            print(f"\nProcessing complete:")
            print(f"  Total audio: {total_duration:.2f}s")
            print(f"  Segments: {len(segments)}")
            print(f"  Processing time: {processing_time:.2f}s")
            print(f"  Real-time factor: {processing_time/total_duration:.2f}x")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


class AudioSegment:
    """Represents an audio segment with timestamps."""

    def __init__(
        self,
        audio: np.ndarray,
        start_time: float,
        end_time: float,
        sample_rate: int = 16000,
    ):
        self.audio = audio
        self.start_time = start_time
        self.end_time = end_time
        self.sample_rate = sample_rate
        self.transcription = ""

    def duration(self) -> float:
        """Get the duration of the segment in seconds."""
        return self.end_time - self.start_time


class SamiASRConfig:
    f"""
    Configuration class for Sami ASR processing.

    Default values:
    - silence_threshold: {DEFAULT_SILENCE_THRESHOLD} (RMS threshold for silence detection)
    - min_silence_duration: {DEFAULT_MIN_SILENCE_DURATION}s (minimum silence duration)
    - min_segment_duration: {DEFAULT_MIN_SEGMENT_DURATION}s (minimum segment duration)
    - max_segment_duration: {DEFAULT_MAX_SEGMENT_DURATION}s (maximum segment duration)
    """

    def __init__(self):
        self.target_sample_rate = 16000
        self.silence_threshold = (
            DEFAULT_SILENCE_THRESHOLD  # RMS threshold for silence detection
        )
        self.min_silence_duration = (
            DEFAULT_MIN_SILENCE_DURATION  # Minimum silence duration in seconds
        )
        self.min_segment_duration = (
            DEFAULT_MIN_SEGMENT_DURATION  # Minimum segment duration in seconds
        )
        self.max_segment_duration = (
            DEFAULT_MAX_SEGMENT_DURATION  # Maximum segment duration in seconds
        )
        self.hop_length = 512  # For librosa analysis
        self.frame_length = 2048  # For librosa analysis


class SamiASR:
    """Enhanced Sami ASR processor with segmentation and multi-format support."""

    def __init__(self, config: SamiASRConfig, verbose: bool = False):
        self.config = config
        self.verbose = verbose
        self.processor = None
        self.model = None

        # Detect available device
        if torch.cuda.is_available():
            self.device = torch.device("cuda")
            self.device_name = torch.cuda.get_device_name()
        else:
            self.device = torch.device("cpu")
            self.device_name = "CPU"

        self._load_model()

    def _load_model(self):
        """Load the Wav2Vec2 model and processor."""
        try:

            if self.verbose:
                print(f"Loading model from: {sami_model_path}")

            if not sami_model_path.exists():
                raise FileNotFoundError(f"Model not found at {sami_model_path}")

            self.processor = Wav2Vec2Processor.from_pretrained(sami_model_path)
            self.model = Wav2Vec2ForCTC.from_pretrained(sami_model_path)

            # Move model to the detected device
            self.model = self.model.to(self.device)

            if self.verbose:
                print("Model loaded successfully!")
                print(f"Model moved to: {self.device}")

        except Exception as e:
            print(f"Error loading model: {e}")
            sys.exit(1)

    def load_audio(self, file_path: str) -> Tuple[np.ndarray, float]:
        """
        Load audio file and convert to the required format.

        Returns:
            Tuple of (audio_array, duration_in_seconds)
        """
        try:
            if self.verbose:
                print(f"Loading audio file: {file_path}")

            # Load audio with librosa (handles multiple formats)
            audio_start_time = time.time()
            audio_array, original_sr = librosa.load(
                file_path, sr=self.config.target_sample_rate, mono=True
            )
            global audio_loading_duration
            audio_loading_duration = time.time() - audio_start_time

            duration = len(audio_array) / self.config.target_sample_rate

            if self.verbose:
                print(
                    f"Audio loaded: {duration:.2f}s, {self.config.target_sample_rate}Hz"
                )

            return audio_array, duration

        except Exception as e:
            raise RuntimeError(f"Failed to load audio file '{file_path}': {e}")

    def detect_silence(self, audio: np.ndarray) -> List[Tuple[float, float]]:
        """
        Detect silence periods in audio using RMS energy analysis.

        Returns:
            List of (start_time, end_time) tuples for silence periods
        """
        silence_start_time = time.time()

        # Calculate RMS energy for each frame
        rms = librosa.feature.rms(
            y=audio,
            frame_length=self.config.frame_length,
            hop_length=self.config.hop_length,
        )[0]

        # Convert frame indices to time
        times = librosa.frames_to_time(
            np.arange(len(rms)),
            sr=self.config.target_sample_rate,
            hop_length=self.config.hop_length,
        )

        # Identify silent frames
        silent_frames = rms < self.config.silence_threshold

        # Find continuous silence periods
        silence_periods = []
        silence_start = None

        for i, (frame_time, is_silent) in enumerate(zip(times, silent_frames)):
            if is_silent and silence_start is None:
                silence_start = frame_time
            elif not is_silent and silence_start is not None:
                silence_duration = frame_time - silence_start
                if silence_duration >= self.config.min_silence_duration:
                    silence_periods.append((silence_start, frame_time))
                silence_start = None

        # Handle silence at the end
        if silence_start is not None:
            silence_duration = times[-1] - silence_start
            if silence_duration >= self.config.min_silence_duration:
                silence_periods.append((silence_start, times[-1]))

        global silence_detection_duration
        silence_detection_duration += time.time() - silence_start_time

        return silence_periods

    def segment_audio(
        self, audio: np.ndarray, no_segment: bool = False
    ) -> List[AudioSegment]:
        """
        Segment audio based on silence detection.

        Args:
            audio: Input audio array
            no_segment: If True, return the entire audio as one segment

        Returns:
            List of AudioSegment objects
        """
        segmentation_start_time = time.time()
        total_duration = len(audio) / self.config.target_sample_rate

        if no_segment:
            return [
                AudioSegment(audio, 0.0, total_duration, self.config.target_sample_rate)
            ]

        if self.verbose:
            print("Detecting silence periods...")

        silence_periods = self.detect_silence(audio)

        if self.verbose:
            print(f"Found {len(silence_periods)} silence periods")

        segments = []
        segment_start = 0.0

        for silence_start, silence_end in silence_periods:
            # Create segment including the silence at the end
            segment_duration = silence_end - segment_start

            # Only create segment if it meets minimum duration
            if segment_duration >= self.config.min_segment_duration:
                start_sample = int(segment_start * self.config.target_sample_rate)
                end_sample = int(silence_end * self.config.target_sample_rate)

                segment_audio = audio[start_sample:end_sample]
                segments.append(
                    AudioSegment(
                        segment_audio,
                        segment_start,
                        silence_end,
                        self.config.target_sample_rate,
                    )
                )

                # Update start for next segment (begins after this silence)
                segment_start = silence_end

        # Handle final segment
        if segment_start < total_duration:
            final_duration = total_duration - segment_start
            if final_duration >= self.config.min_segment_duration:
                start_sample = int(segment_start * self.config.target_sample_rate)
                segment_audio = audio[start_sample:]
                segments.append(
                    AudioSegment(
                        segment_audio,
                        segment_start,
                        total_duration,
                        self.config.target_sample_rate,
                    )
                )

        # If no segments were created, return the entire audio
        if not segments:
            segments = [
                AudioSegment(audio, 0.0, total_duration, self.config.target_sample_rate)
            ]

        if self.verbose:
            print(f"Created {len(segments)} audio segments")

        global segmentation_duration
        segmentation_duration = time.time() - segmentation_start_time

        return segments

    def transcribe_segment(self, segment: AudioSegment) -> str:
        """Transcribe a single audio segment."""
        try:
            inference_start_time = time.time()

            # Tokenize
            input_values = self.processor(
                segment.audio,
                return_tensors="pt",
                padding="longest",
                sampling_rate=segment.sample_rate,
            ).input_values

            # Move input tensors to the same device as the model
            input_values = input_values.to(self.device)

            # Get logits
            with torch.no_grad():
                logits = self.model(input_values).logits

            # Decode
            predicted_ids = torch.argmax(logits, dim=-1)
            transcription = self.processor.batch_decode(predicted_ids)[0]

            global inference_duration
            inference_duration += time.time() - inference_start_time

            return transcription.strip()

        except Exception as e:
            if self.verbose:
                print(f"Error transcribing segment: {e}")
            return "[TRANSCRIPTION_ERROR]"

    def process_file(
        self, file_path: str, no_segment: bool = False
    ) -> List[AudioSegment]:
        """
        Process an audio file and return transcribed segments.

        Args:
            file_path: Path to the audio file
            no_segment: If True, disable segmentation

        Returns:
            List of transcribed AudioSegment objects
        """
        # Load audio
        audio, duration = self.load_audio(file_path)

        # Segment audio
        segments = self.segment_audio(audio, no_segment)

        # Transcribe each segment
        if self.verbose:
            print(f"Transcribing {len(segments)} segments...")

        for i, segment in enumerate(segments):
            if self.verbose:
                print(f"Transcribing segment {i+1}/{len(segments)}")

            segment.transcription = self.transcribe_segment(segment)

        return segments


def format_timestamp(seconds: float) -> str:
    """Format seconds as MM:SS.mmm"""
    minutes = int(seconds // 60)
    seconds = seconds % 60
    return f"{minutes:02d}:{seconds:06.3f}"


def print_whisper_style(segments: List[AudioSegment]):
    """Print transcription in Whisper-style format."""
    for segment in segments:
        start_str = format_timestamp(segment.start_time)
        end_str = format_timestamp(segment.end_time)
        print(f"[{start_str} -> {end_str}] {segment.transcription}")


def output_json(segments: List[AudioSegment], file_path: str):
    """Output transcription as JSON."""
    data = {
        "segments": [
            {
                "start": segment.start_time,
                "end": segment.end_time,
                "duration": segment.duration(),
                "text": segment.transcription,
            }
            for segment in segments
        ]
    }

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
