from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class CodeSubmission(models.Model):
    user: User = models.ForeignKey(User, on_delete=models.CASCADE)  # Authenticated User
    language = models.CharField(max_length=50)
    code = models.TextField()
    user_input = models.TextField(blank=True, null=True)  # Optional user input
    output = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)  # Stores submission time

    def __str__(self):
        return f"{self.user} - {self.language} - {self.timestamp}"
