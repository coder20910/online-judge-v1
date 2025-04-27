from django.db import models
from django.contrib.auth.models import User
from problems.models import Problems  # Adjust if your Problem model is elsewhere

# Create your models here.
VERDICT_CHOICES = [
    ("Accepted", "Accepted"),
    ("Wrong Answer", "Wrong Answer"),
    ("Runtime Error", "Runtime Error"),
    ("Time Limit Exceeded", "Time Limit Exceeded"),
    ("Compilation Error", "Compilation Error"),
    ("Error", "Error"),
]

class CodeSubmission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    problem = models.ForeignKey(Problems, on_delete=models.CASCADE, null=True)
    language = models.CharField(max_length=50)
    code = models.TextField()
    user_input = models.TextField(blank=True, null=True)
    output = models.TextField()
    verdict = models.CharField(max_length=50, choices=VERDICT_CHOICES, null=True)
    verdict_details = models.TextField(blank=True, null=True, help_text="Detailed verdict info like failed test case")
    execution_time = models.FloatField(null=True, blank=True, help_text="Execution time in seconds")
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.problem} - {self.verdict}"

class UserCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    problem = models.ForeignKey(
        Problems,
        on_delete=models.CASCADE,
        related_name='user_codes'
    )
    code = models.TextField(blank=True)
    language = models.CharField(max_length=20)
    last_modified = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'problem', 'language']
        ordering = ['-last_modified']

    def __str__(self):
        return f"{self.user.username}'s {self.language} code for {self.problem.title}"
