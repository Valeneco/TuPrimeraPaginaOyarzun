from django.db import models
from ckeditor.fields import RichTextField  # Si quieres contenido enriquecido

class Page(models.Model):
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=200, blank=True)
    content = RichTextField()
    image = models.ImageField(upload_to='pages/', blank=True, null=True)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.title


# Create your models here.
