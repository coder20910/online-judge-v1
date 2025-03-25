from django.db import models

# Create your models here.
class Problems(models.Model):
    title = models.CharField(max_length=200)
    difficulty = models.CharField(max_length=50, blank=True) #blank means optional
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.title)
