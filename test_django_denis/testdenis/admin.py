from django.contrib import admin

from .models import School, Class, Student, Teacher, Course


admin.site.register(School)
admin.site.register(Class)
admin.site.register(Student)
admin.site.register(Teacher)
admin.site.register(Course)
