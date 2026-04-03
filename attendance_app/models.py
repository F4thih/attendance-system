from django.db import models

class Student(models.Model):
    name = models.CharField(max_length=100)
    admn_no = models.CharField(max_length=7, unique=True)

    def __str__(self):
        return f"{self.name} ({self.admn_no})"


class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    date = models.DateField()
    time = models.TimeField(auto_now_add=True)
    status = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['student', 'date'],
                name='unique_attendance_per_day'
            )
        ]

    def __str__(self):
        return f"{self.student.name} - {self.date} - Present"
