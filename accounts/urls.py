"""accounts URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include, re_path
from . import views

urlpatterns = [
    path('student_login/', views.student_login, name='student_login'),
    path('teacher_login/', views.teacher_login, name='teacher_login'),
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('teacher/dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('logout/', views.student_logout_view, name='student_logout'),
    path('teacher/logout/', views.teacher_logout_view, name='teacher_logout'),
    path('student/dashboard/personal_information', views.personal_info, name='personal_info'),
    path('teacher/dashboard/personal_information', views.teacher_personal_info, name='teacher_personal_info'),
    path('student/dashboard/contact_information', views.contact_info, name='contact_info'),
    path('teacher/dashboard/contact_information', views.teacher_contact_info, name='teacher_contact_info'),
    path('student/dashboard/training_data', views.training_data, name='training_data'),
    path('teacher/dashboard/teaching_data', views.teaching_data, name='teacher_data'),
    path('student/dashboard/class_schedule', views.class_schedule_view, name='class_schedule_view'),
    path('teacher/dashboard/class_schedule', views.teacher_class_schedule_view, name='teacher_class_schedule'),
    path('student/dashboard/gradebook', views.gradebook, name='gradebook'),
    path('teacher/dashboard/gradebook', views.teacher_gradebook, name='teacher_gradebook'),
    path('student/dashboard/grade_average', views.grade_average, name='grade_average'),
    path('student/dashboard/subjects_taken', views.subjects_taken, name='subjects_taken'),
    path('teacher/dashboard/subject_taught', views.teacher_subjects_taught, name='teacher_subjects_taught'),
    path('student/dashboard/midterm', views.midterm, name='midterm'),
    path('teacher/dashboard/midterm', views.teacher_midterm, name='teacher_midterm'),
    path('student/dashboard/taken_exams', views.taken_exams, name='taken_exams'),
    path('teacher/dashboard/exam_results', views.teacher_exam_results, name='teacher_exam_results'),
    path('teacher/dashboard/attendance', views.teacher_attendance, name='teacher_attendance'),
    path('student/dashboard/attendance', views.student_attendance, name='student_attendance'),
    path('student/dashboard/payment', views.payment, name='payment'),
    path('student/dashboard/invoices', views.invoice, name='invoices'),
    path('student/dashboard/textbooks', views.textbook, name='textbook'),
    path('student/dashboard/textbooks', views.textbook, name='textbook'),
    path('student/dashboard/calendar', views.calendar, name='calendar'),
    path('student/dashboard/report_card', views.report_card, name='report_card'),
    path('student/dashboard/transcripts', views.transcripts, name='transcripts'),
    path('student/dashboard/inbox', views.student_inbox, name='inbox'),
    path('student/dashboard/sent', views.student_sent, name='sent'),
    path('student/dashboard/compose', views.student_compose, name='compose'),
    path('student/dashboard/sent/message', views.student_sent_message_view, name='sent_message_view'),
    path('student/dashboard/settings', views.navbar_settings, name='navbar_settings'),
    path('student/dashboard/change_password', views.student_change_password, name='student_change_password'),
    path('teacher/dashboard/change_password', views.teacher_change_password, name='teacher_change_password'),
    path('admin/login', views.admin_login, name='admin_login'),
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/logout', views.admin_logout, name='admin_logout'),
    path('admin/dashboard/add-new-student', views.admin_new_student, name='admin_add_new_student'),
    path('admin/dashboard/add-new-teacher', views.admin_new_teacher, name='admin_add_new_teacher'),
    path('admin/dashboard/add-class-schedule', views.add_class_schedule, name='admin_add_class_schedule'),
    path('admin/dashboard/modify-student', views.modify_student, name='admin_modify_student'),
    path('admin/dashboard/modify-teacher', views.modify_teacher, name='admin_modify_teacher'),
    path('admin/dashboard/reset-password', views.reset_password, name='admin_reset_password'),
    path('admin/dashboard/add_payment', views.admin_add_payment, name='admin_add_payment'),
    path('admin/dashboard/add_student_payment_record', views.admin_add_student_payment, name='admin_add_student_payment'),
    path('admin/dashboard/add_textbook', views.admin_add_textbook, name='admin_add_textbook'),
    path('admin/dashboard/modify_textbook', views.admin_modify_textbook, name='admin_modify_textbook'),
    path('admin/dashboard/modify_class_schedule', views.admin_modify_class_schedule, name='admin_modify_class_schedule'),
    path('admin/dashboard/modify_payment', views.admin_modify_payment, name='admin_modify_payment'),
    path('admin/dashboard/modify_student_class', views.modify_student_class, name='admin_modify_student_class'),
    path('admin/dashboard/modify_subjects_taught', views.admin_modify_subjects_taught, name='admin_modify_subjects_taught'),
]
