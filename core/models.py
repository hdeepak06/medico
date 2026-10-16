from django.db import models
from django.utils.text import slugify

class Specialization(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    icon_name = models.CharField(max_length=50, default='heart-pulse', help_text="Icon identifier like heart, brain, bone, eye, tooth, etc.")
    description = models.TextField(help_text="Brief description of the medical specialty")
    color_accent = models.CharField(max_length=30, default="#0284C7")
    is_featured = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Medical Specialization'
        verbose_name_plural = 'Medical Specializations'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Testimonial(models.Model):
    patient_name = models.CharField(max_length=100)
    patient_location = models.CharField(max_length=100, blank=True, default="New York, USA")
    avatar = models.CharField(max_length=255, blank=True, help_text="Image URL or relative path")
    doctor_treated = models.CharField(max_length=100, blank=True)
    rating = models.IntegerField(default=5)
    comment = models.TextField()
    is_featured = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.patient_name} - {self.rating} stars"


class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=30, blank=True)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Message from {self.name} - {self.subject}"
