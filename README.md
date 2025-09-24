# Face Stalker

Face Stalker is a Python-based face recognition tool that detects whether a specific person appears in a set of group photos. By providing a reference image of a person and a folder of group images, the script identifies and lists all images where the person is present.

## Features

- Detects a reference face across multiple images
- Supports common image formats: `.jpg`, `.jpeg`, `.png`, `.bmp`, `.tiff`
- Prints a list of filenames where the person is detected
- Easy to set up and run in a virtual environment

## Setup

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd Face-Stalker
   ```

2. **Create and activate a virtual environment**
   ```bash
   python3 -m venv face_env
   source face_env/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install face_recognition dlib opencv-python numpy
   ```

## Usage

1. Place your reference image in the project folder (e.g., `reference.jpg`).
2. Place group photos inside a folder (e.g., `group_images/`).
3. Run the script:
   ```bash
   python main.py
   ```
4. The script will output the list of images where the reference person is detected.