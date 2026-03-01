from django.db import models

class UserProfile(models.Model):
    username = models.CharField(max_length=100, unique=True)
    eye_color = models.CharField(max_length=50, default='blue')

    def __str__(self):
        return self.username

class ScreenTime(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='screentime_records')
    device_type = models.CharField(max_length=20) # 'desktop' or 'mobile'
    seconds = models.PositiveBigIntegerField(default=0)

    class Meta:
        unique_together = ('user', 'device_type')

    def __str__(self):
        return f"{self.user.username} - {self.device_type}: {self.seconds}s"
