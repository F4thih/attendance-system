from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("scan/", views.scan_page, name="scan_page"),
    path("live-scan/", views.live_scan, name="live_scan"),
    path("attendance/", views.attendance_status, name="attendance_status"),
    path("attendance/data/", views.attendance_status_data, name="attendance_status_data"),
    path("student/<int:student_id>/", views.student_attendance, name="student_attendance"),
]
