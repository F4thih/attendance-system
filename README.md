# attendance-system


# Smart Attendance System (OCR Based)

A real-time attendance management system built with **Django**, **OpenCV**, and **Tesseract OCR**. This system captures student ID cards via a live webcam feed, extracts the admission number, and automatically updates the attendance record.

-----

## System Architecture

The system follows a Model-View-Template (MVT) structure with an integrated computer vision pipeline.

1.  **Frontend:** A browser-based camera interface captures frames and sends them to the backend via AJAX.
2.  **Processing:** The backend processes the image using OpenCV (Grayscale/Thresholding) and extracts text via Tesseract.
3.  **Validation:** The system uses Regex and Fuzzy Matching to verify the student in the database.
4.  **Feedback:** The UI updates instantly with visual flashes and audio cues.

-----

## Getting Started

### 1\. Prerequisites

  * Python 3.8+
  * [Tesseract OCR Engine](https://www.google.com/search?q=https://github.com/UB-Mannheim/tesseract/wiki) (Install this on your computer).

### 2\. Installation

```bash
# Clone the repository
git clone https://github.com/your-username/attendance-system.git
cd attendance-system

# Install dependencies
pip install django opencv-python numpy pytesseract
```

### 3\. Tesseract Configuration

You **must** tell the app where Tesseract is installed. Open `attendance_app/views.py` and modify this line:

```python
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

### 4\. Database Setup

The database is excluded from this repository for security. Run these commands to create your own:

```bash
python manage.py migrate
python manage.py createsuperuser  # Create an admin account
python manage.py runserver
```

-----

## Configuration & Customization

### How to Change the OCR Logic

The system currently looks for a specific pattern (starting with "SS"). You can modify the **Regex** in `views.py` to match your college's ID format:

  * **Current:** `r'^SS[A-Z0-9]{3,}$'` (Matches "SS" followed by 3+ characters).
  * **Change to 5 digits:** `r'^\d{5}$'`.

### Adjusting Matching Strictness

If the OCR frequently misreads characters (e.g., 'O' as '0'), adjust the `cutoff` value in the `get_close_matches` function in `views.py`:

  * **0.90 (Current):** Very strict.
  * **0.75:** More lenient, better for low-quality cameras.

### Connecting Sounds & Images

  * **Sounds:** Replace files in `static/attendance_app/sound/` (`success.mp3`, `already.mp3`, `failed.mp3`).
  * **Background:** Replace `static/attendance_app/bg.jpeg`.

-----

## Security Note

  * **SECRET\_KEY:** For production, move the `SECRET_KEY` in `settings.py` to an environment variable.
  * **HTTPS:** The camera feature requires HTTPS when hosted on a live server (local development on `localhost` is fine).

-----

## Project Structure

  * `attendance_app/` - Contains the OCR logic (`views.py`) and database models.
  * `templates/` - HTML files for the scanner and dashboard.
  * `static/` - CSS, Images, and Audio feedback files.

-----

### Part 3: Connecting the Sounds (Technical Detail)

To ensure the sounds work, verify your folder structure looks like this:

```text
static/
└── attendance_app/
    ├── bg.jpeg
    └── sound/
        ├── success.mp3
        ├── already.mp3
        └── failed.mp3
```

In `scan.html`, the JavaScript automatically looks for these files when the server returns a specific status. If you change the filenames, you must also update the variable names in the `<script>` tag of `scan.html`.