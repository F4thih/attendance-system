from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from datetime import date, timedelta
import re
import cv2
import numpy as np
import pytesseract
from difflib import get_close_matches
from .models import Student, Attendance
from django.core.serializers import serialize
from django.utils.timezone import localtime

# Windows Tesseract path
pytesseract.pytesseract.tesseract_cmd = r"C:\Path\To\tesseract.exe"


def index(request):
    """Landing page"""
    return render(request, "attendance_app/index.html")

def scan_page(request):
    """Live camera scanning page"""
    return render(request, "attendance_app/scan.html")

def attendance_status_data(request):
    today = date.today()
    present_attendance = Attendance.objects.filter(
        date=today,
        status=True
    ).select_related("student")

    present_data = [
        {
            "id": att.student.id,
            "name": att.student.name,
            "admn_no": att.student.admn_no,
            "time": att.time.strftime("%I:%M %p") if att.time else "--:--"  # 12-hour format
        } for att in present_attendance
    ]

    present_ids = [att.student.id for att in present_attendance]
    absent_students = Student.objects.exclude(id__in=present_ids)
    absent_data = [
        {"id": s.id, "name": s.name, "admn_no": s.admn_no} for s in absent_students
    ]

    return JsonResponse({"present": present_data, "absent": absent_data})

def attendance_status(request):
    """Attendance dashboard"""
    today = date.today()

    present_attendance = Attendance.objects.filter(
        date=today,
        status=True
    ).select_related("student")

    present_student_ids = present_attendance.values_list(
        "student_id", flat=True
    )

    absent_students = Student.objects.exclude(id__in=present_student_ids)

    return render(request, "attendance_app/attendance_status.html", {
        "today": today,
        "present_attendance": present_attendance,
        "absent_students": absent_students
    })


def student_attendance(request, student_id):
    student = get_object_or_404(Student, id=student_id)

    end_date = date.today()
    start_date = end_date - timedelta(days=29)

    attendance_qs = Attendance.objects.filter(
        student=student,
        date__range=(start_date, end_date)
    )

    attendance_map = {att.date: att for att in attendance_qs}

    attendance_list = []
    current_date = start_date
    while current_date <= end_date:
        if current_date in attendance_map:
            attendance_list.append({
                "date": current_date,
                "status": "Present",
                "time": attendance_map[current_date].time
            })
        else:
            attendance_list.append({
                "date": current_date,
                "status": "Absent",
                "time": None
            })
        current_date += timedelta(days=1)

    return render(request, "attendance_app/student_attendance.html", {
        "student": student,
        "attendance_list": attendance_list
    })


@csrf_exempt
def live_scan(request):
    """Strict live camera OCR for SS-prefixed admission numbers"""

    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Invalid request"})

    #  Get uploaded image
    image_file = request.FILES.get("id_card")
    if not image_file:
        return JsonResponse({"status": "error", "message": "No image uploaded"})

    #  Convert to OpenCV image
    img_bytes = np.frombuffer(image_file.read(), np.uint8)
    img = cv2.imdecode(img_bytes, cv2.IMREAD_COLOR)

    if img is None:
        return JsonResponse({"status": "error", "message": "Invalid image"})

    #  OCR Preprocessing
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (3, 3), 0)
    gray = cv2.equalizeHist(gray)

    thresh = cv2.adaptiveThreshold(
        gray,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        25,
        10
    )

    kernel = np.ones((2, 2), np.uint8)
    thresh = cv2.dilate(thresh, kernel, iterations=1)

    # OCR
    config = "--oem 3 --psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    raw_text = pytesseract.image_to_string(thresh, config=config)

    print("========== OCR RAW TEXT ==========")
    print(raw_text)

    # Extract SS-prefixed admission number
    admn_no = None

    for line in raw_text.splitlines():
        clean = re.sub(r'[^A-Z0-9]', '', line.upper())

        # STRICT FORMAT: SS followed by at least 4 characters
        if re.match(r'^SS[A-Z0-9]{3,}$', clean):
            admn_no = clean
            break

    if not admn_no:
        return JsonResponse({
            "status": "error",
            "message": "Valid SS admission number not detected"
        })

    # Exact match first (SAFE)
    student = Student.objects.filter(admn_no__iexact=admn_no).first()

    # Very strict fuzzy match fallback
    if not student:
        db_adms = list(Student.objects.values_list("admn_no", flat=True))
        db_adms_upper = [a.upper() for a in db_adms]

        matches = get_close_matches(
            admn_no,
            db_adms_upper,
            n=1,
            cutoff=0.90  # VERY STRICT
        )

        if not matches:
            return JsonResponse({
                "status": "error",
                "message": f"Student not found ({admn_no})"
            })

        student = Student.objects.get(admn_no__iexact=matches[0])

    # Mark attendance
    today = date.today()
    attendance, created = Attendance.objects.get_or_create(
        student=student,
        date=today,
        defaults={"status": True}
    )

    # Return response for frontend
    if created:
        return JsonResponse({
            "status": "success",
            "message": f"{student.name} marked present"
        })
    else:
        return JsonResponse({
            "status": "already",
            "message": f"{student.name} already marked present"
        })
