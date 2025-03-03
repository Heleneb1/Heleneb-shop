from django.db import models
from django.urls import reverse

# Create your models here.
class Category(models.Model):
    name= models.CharField(max_length=100)
    slug= models.SlugField(max_length=100)
    description= models.TextField(blank=True)
    image=models.ImageField(upload_to='categories',blank=True , null=True)

    def __str__(self):
        return self.name
    def get_absolute_url(self):
        return reverse('category', kwargs={'slug':self.slug})
    
class Size(models.Model):
    name= models.CharField(max_length=100)
    
    def __str__(self):
        return self.name