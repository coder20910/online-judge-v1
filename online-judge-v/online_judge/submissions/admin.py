from django.contrib import admin
from submissions.models import CodeSubmission, UserCode
# Register your models here.

admin.site.register(CodeSubmission)
admin.site.register(UserCode)