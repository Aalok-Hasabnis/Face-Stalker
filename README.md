# Face Stalker

Face Stalker is a Python-based face recognition tool that detects whether a specific person appears in a set of group photos. It identifies matches using face embeddings, organizes results by face similarity and filename, and detects mislabeled images.

## Features

- Detects faces using 128-dimensional embeddings with ChromaDB storage
- Dual categorization: by face similarity and by filename
- Identifies mislabeled images automatically
- Supports `.jpg`, `.jpeg`, `.png`, `.bmp`, `.tiff`, `.webp`

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
   pip install face_recognition chromadb sentence-transformers pillow numpy
   ```

## Usage

1. Place your reference image in the project folder (e.g., `reference.jpg`)
2. Place group photos inside `group_images/` folder
3. Update `main.py`:
   ```python
   reference_image = "reference.jpg"  # Change this
   ```
4. Run the script:
   ```bash
   python main.py
   ```

## Output

The script provides three views:
- **Face Similarity**: All images matching the reference face
- **Filename Groups**: Images organized by their filename
- **Mislabeling**: Images where face doesn't match filename

## Configuration

Adjust sensitivity in `main.py`:
```python
similarity_threshold=0.4,    # Lower = more results (0.0-1.0)
filename_weight=0.4          # Higher = prioritize filename matching
```

## Tips

- Name files: `person.jpg`, `person1.jpg`, `person_name2.jpg`
- Use clear, front-facing photos
- Lower `similarity_threshold` to 0.3 for more matches
- Delete `chroma_db/` folder to reset database