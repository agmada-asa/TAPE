# TAPE – Podcast Clip Generator

TAPE (Transcribe Audio, Process Exports) is an automated desktop application designed to streamline the podcast post-production workflow. By chaining together high-accuracy transcription and advanced semantic analysis, TAPE significantly reduces the time required to identify and extract viral clips from long-form audio and video.

## Features

- **High-Accuracy Transcription:** Utilizes OpenAI's **Whisper** model to automatically transcribe `.mp3` and `.mp4` files into accurate `.srt` subtitle files.
- **Semantic Content Analysis:** Integrates **Llama 3.2** (via Ollama) to analyze transcripts and intelligently generate engaging, timestamped ideas for social media posts (Instagram Reels, TikToks, etc.).
- **Automated Workflow:** Replaces manual searching with an automated pipeline, requiring only human verification of the AI-generated clips.
- **Easy-to-Use GUI:** Simple, thread-safe Tkinter graphical interface for easy file selection and processing without touching the command line.

## Prerequisites

- **Python 3.8+**
- **Ollama:** You must have [Ollama](https://ollama.com/) installed and running locally with the `llama3.2` model pulled.
  ```bash
  ollama pull llama3.2
  ```
- **FFmpeg:** Required by Whisper for audio processing. (e.g., `brew install ffmpeg` on macOS, or `apt install ffmpeg` on Linux).

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/YOUR_USERNAME/TAPE.git
   cd TAPE
   ```
2. Create and activate a virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Ensure your local Ollama instance is running.
2. Run the main application:
   ```bash
   python main.py
   ```
3. Use the GUI to browse for an `.mp3` or `.mp4` file.
4. Click **Start Transcription**. The application will:
   - Generate a `.srt` subtitle file in the same directory as the source.
   - Generate a `* content ideas.md` file containing viral clip suggestions with timestamps.
5. The output directory will automatically open in Finder/Explorer once completed.

## Building the App (macOS / Windows)

To package the application into a standalone executable:
```bash
python pyinstaller.py
```
This will generate a `dist` folder. You can move the resulting application file to your Applications folder for quick access.