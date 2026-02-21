from django.db import models

class SavedItem(models.Model):
    URL_TYPE_CHOICES = [
        ('instagram', 'Instagram'),
        ('twitter', 'Twitter'),
        ('blog', 'Blog/Article'),
        ('other', 'Other'),
    ]

    url = models.URLField(max_length=500, unique=True)
    item_type = models.CharField(max_length=20, choices=URL_TYPE_CHOICES, default='other')
    title = models.CharField(max_length=255, blank=True, null=True)
    caption = models.TextField(blank=True, null=True)
    summary = models.TextField(blank=True, null=True)
    category = models.CharField(max_length=100, blank=True, null=True)  # AI generated
    hashtags = models.JSONField(default=list, blank=True)
    media_url = models.URLField(max_length=500, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title or self.url
