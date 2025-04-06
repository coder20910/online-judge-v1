from django.db import models

# Create your models here.
class Problems(models.Model):
    title = models.CharField(max_length=200)
    difficulty = models.CharField(max_length=50, blank=True) #blank means optional
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.title)

class TestCase(models.Model):
    problem = models.ForeignKey(Problems, on_delete=models.CASCADE, related_name="testcases")
    input_data = models.TextField()
    output_data = models.TextField()
    is_public = models.BooleanField(default=False)
    is_sample = models.BooleanField(default=False)
