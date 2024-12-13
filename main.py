import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import whisper
from datetime import datetime
from docx import Document
import subprocess

# Helper functions
def open_directory_in_finder(path):
    try:
        subprocess.run(["open", path], check=True)
        print(f"Directory '{path}' opened successfully in Finder.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to open directory '{path}': {e}")

def format_timestamp(seconds: float) -> str:
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    milliseconds = int((seconds - int(seconds)) * 1000)
    return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"

def transcribe_audio(audio_file_path: str) -> dict:
    model = whisper.load_model("medium")
    return model.transcribe(audio_file_path)

def write_srt_file(transcript: dict, srt_file_path: str):
    segments = transcript["segments"]
    with open(srt_file_path, "w", encoding="utf-8") as srt_file:
        for i, segment in enumerate(segments):
            start_time = format_timestamp(segment["start"])
            end_time = format_timestamp(segment["end"])
            text = segment["text"].strip()
            srt_file.write(f"{i + 1}\n")
            srt_file.write(f"{start_time} --> {end_time}\n")
            srt_file.write(f"{text}\n\n")

def write_docx_file(transcript: dict, doc_file_path: str):
    doc = Document()
    segments = transcript["segments"]
    for i, segment in enumerate(segments):
        start_time = format_timestamp(segment["start"])
        end_time = format_timestamp(segment["end"])
        text = segment["text"].strip()
        doc.add_paragraph(f"{i + 1}\n{start_time} --> {end_time}\n{text}\n\n")
    doc.save(doc_file_path)

# GUI functions
def browse_file():
    file_path = filedialog.askopenfilename(
        filetypes=[("Audio/Video Files", "*.mp3 *.mp4"), ("All Files", "*.*")]
    )
    if file_path:
        file_entry.delete(0, tk.END)
        file_entry.insert(0, file_path)

def transcribe_in_thread(file_path):
    start = datetime.now()
    try:
        transcript = transcribe_audio(file_path)

        # Generate output file paths
        srt_output_path = file_path.replace(".mp3", ".srt").replace(".mp4", ".srt")
        doc_output_path = file_path.replace(".mp3", ".docx").replace(".mp4", ".docx")

        # Write SRT and DOCX files
        write_srt_file(transcript, srt_output_path)
        write_docx_file(transcript, doc_output_path)

        end = datetime.now()
        duration = end - start
        status_label.config(text=f"Transcription completed in {duration}.\nSRT: {srt_output_path}\nDOCX: {doc_output_path}")
        messagebox.showinfo("Status Update", "Transcription Finished")
        open_directory_in_finder(doc_output_path)
    except Exception as e:
        status_label.config(text=f"Error: {e}")

def start_transcription():
    file_path = file_entry.get()
    if not file_path:
        messagebox.showwarning("No File", "Please select a file to transcribe.")
        return

    # Update the status label
    status_label.config(text="Transcribing... Please wait.")
    window.update()  # Force UI update

    # Start transcription in a new thread
    transcription_thread = threading.Thread(target=transcribe_in_thread, args=(file_path,))
    transcription_thread.start()

# Tkinter setup
window = tk.Tk()
window.title("TAPE")

# File selection
file_label = tk.Label(window, text="Select an audio or video file:")
file_label.pack(pady=5)

file_entry = tk.Entry(window, width=50)
file_entry.pack(pady=5)

browse_button = tk.Button(window, text="Browse", command=browse_file)
browse_button.pack(pady=5)

# Transcription button
transcribe_button = tk.Button(window, text="Start Transcription", command=start_transcription)
transcribe_button.pack(pady=20)

# Status label
status_label = tk.Label(window, text="", wraplength=400, justify="left")
status_label.pack(pady=10)

# Run the Tkinter event loop
window.mainloop()
