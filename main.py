"""
main.py

The main GUI application for TAPE (Transcribe Audio, Process Exports).
Provides a Tkinter interface to select audio/video files, transcribe them using
OpenAI's Whisper model, and generate social media content ideas using Llama 3.2.
"""

import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import whisper
from datetime import datetime
import subprocess
import os

from generateIdeas import generate_content_ideas


# ========================================== #
#             Helper Functions               #
# ========================================== #

def open_directory_in_finder(path: str) -> None:
    """
    Opens the specified directory in the macOS Finder (or default file explorer).

    Args:
        path (str): The absolute path to the directory to open.
    """
    try:
        # Note: 'open' is a macOS command. For cross-platform support, 
        # consider using 'xdg-open' on Linux and 'explorer' on Windows.
        subprocess.run(["open", path], check=True)
        print(f"Directory '{path}' opened successfully in Finder.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to open directory '{path}': {e}")
    except FileNotFoundError:
        print(f"Command 'open' not found. Ensure you are on a compatible OS.")

def format_timestamp(seconds: float) -> str:
    """
    Converts a time duration in seconds to the SRT timestamp format.

    Args:
        seconds (float): Duration in seconds.

    Returns:
        str: Timestamp string formulated as 'HH:MM:SS,mmm'.
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds_remainder = int(seconds % 60)
    milliseconds = int((seconds - int(seconds)) * 1000)
    return f"{hours:02}:{minutes:02}:{seconds_remainder:02},{milliseconds:03}"

def transcribe_audio(audio_file_path: str) -> dict:
    """
    Transcribes the given audio or video file using the Whisper 'medium' model.

    Args:
        audio_file_path (str): The absolute path to the audio or video file.

    Returns:
        dict: The transcription result dictionary returned by Whisper, which
              includes the full text and individual segments with timestamps.
    """
    model = whisper.load_model("medium")
    return model.transcribe(audio_file_path)

def write_srt_file(transcript: dict, srt_file_path: str) -> None:
    """
    Takes a Whisper transcription dictionary and writes it to a standard .srt file.

    Args:
        transcript (dict): The Whisper transcription result.
        srt_file_path (str): The path where the .srt file will be saved.
    """
    segments = transcript.get("segments", [])
    with open(srt_file_path, "w", encoding="utf-8") as srt_file:
        for i, segment in enumerate(segments):
            start_time = format_timestamp(segment["start"])
            end_time = format_timestamp(segment["end"])
            text = segment["text"].strip()
            
            # Write SRT standard block format
            srt_file.write(f"{i + 1}\n")
            srt_file.write(f"{start_time} --> {end_time}\n")
            srt_file.write(f"{text}\n\n")

def write_content_file(ideas: list, path: str) -> None:
    """
    Writes the list of generated content ideas to a Markdown file.

    Args:
        ideas (list): A list of strings, each containing generated text for content ideas.
        path (str): The path where the Markdown file will be saved.
    """
    with open(path, "w", encoding="utf-8") as content_file:
        for idea in ideas:
            content_file.write(f"{idea}\n")


# ========================================== #
#               GUI Functions                #
# ========================================== #

def browse_file() -> None:
    """
    Opens a file dialog for the user to select an audio or video file,
    and updates the UI entry widget with the selected file path.
    """
    file_path = filedialog.askopenfilename(
        title="Select Media",
        filetypes=[("Audio/Video Files", "*.mp3 *.mp4"), ("All Files", "*.*")]
    )
    if file_path:
        file_entry.delete(0, tk.END)
        file_entry.insert(0, file_path)

def transcribe_in_thread(file_path: str) -> None:
    """
    The background task that runs the transcription and idea generation models.
    This runs in a separate thread to prevent the Tkinter GUI from freezing.

    Args:
        file_path (str): Path to the media file to process.
    """
    start_time = datetime.now()
    try:
        # 1. Transcribe the audio using OpenAI Whisper
        transcript = transcribe_audio(file_path)

        # Generate output file paths based on the input filename
        base_path_lower = file_path.lower()
        if base_path_lower.endswith(".mp3"):
            srt_output_path = file_path[:-4] + ".srt"
            content_output_path = file_path[:-4] + " content ideas.md"
        elif base_path_lower.endswith(".mp4"):
            srt_output_path = file_path[:-4] + ".srt"
            content_output_path = file_path[:-4] + " content ideas.md"
        else:
            # Fallback for unexpected extensions
            srt_output_path = file_path + ".srt"
            content_output_path = file_path + " content ideas.md"

        # 2. Save the transcription to an SRT file
        write_srt_file(transcript, srt_output_path)

        end_time = datetime.now()
        duration = end_time - start_time
        
        # Update status immediately after transcription completes
        status_label.config(
            text=f"Transcription completed in {duration}.\nGenerating content ideas..."
        )

        # 3. Chain into Llama 3.2 for semantic content analysis based on the SRT
        ideas = generate_content_ideas(srt_output_path)
        write_content_file(ideas, content_output_path)

        status_label.config(
            text=f"Process completed successfully in {duration}.\nSRT: {os.path.basename(srt_output_path)}\nIdeas: {os.path.basename(content_output_path)}"
        )

        # Notify user and open the containing folder
        messagebox.showinfo("Status Update", "Transcription and Idea Generation Finished!")
        open_directory_in_finder(os.path.dirname(srt_output_path))
        
    except Exception as e:
        status_label.config(text=f"Error occurred: {str(e)}")
        messagebox.showerror("Error", f"An error occurred during processing:\n{str(e)}")

def start_transcription() -> None:
    """
    Validates user input and launches the transcription thread if a valid file is provided.
    """
    file_path = file_entry.get()
    if not file_path or not os.path.exists(file_path):
        messagebox.showwarning("Invalid File", "Please select a valid file to transcribe.")
        return

    # Update the UI status label to show activity
    status_label.config(text="Transcribing using Whisper... Please wait.")
    window.update()  # Force UI update so text shows before thread starts

    # Run the heavy lifting in a daemon thread so it doesn't block the main event loop
    transcription_thread = threading.Thread(target=transcribe_in_thread, args=(file_path,), daemon=True)
    transcription_thread.start()


# ========================================== #
#               Tkinter Setup                #
# ========================================== #

if __name__ == "__main__":
    # Initialize main window
    window = tk.Tk()
    window.title("TAPE - Podcast Clip Generator")
    window.geometry("500x250")
    window.resizable(False, False)

    # File selection label
    file_label = tk.Label(window, text="Select an audio or video file (.mp3 / .mp4):", font=("Arial", 12))
    file_label.pack(pady=(20, 5))

    # Entry field for file path
    file_entry = tk.Entry(window, width=50)
    file_entry.pack(pady=5)

    # Browse button
    browse_button = tk.Button(window, text="Browse", command=browse_file, width=15)
    browse_button.pack(pady=5)

    # Transcription start button
    transcribe_button = tk.Button(window, text="Start Processing", command=start_transcription, bg="#4CAF50", width=20)
    transcribe_button.pack(pady=10)

    # Label to report processing status or errors
    status_label = tk.Label(window, text="", wraplength=450, justify="center")
    status_label.pack(pady=5)

    # Run the Tkinter main event loop
    window.mainloop()
