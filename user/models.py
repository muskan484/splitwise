import uuid
from django.db import models

class User(models.Model):
    userId = models.CharField(max_length=50, unique=True, blank = True)
    name = models.CharField(max_length=100, blank=False)
    email = models.EmailField(unique=True)
    mobile_number = models.CharField(max_length=10)  

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
            if not self.userId:
                self.userId = self.name.lower().replace(' ', '_') + '_' + str(uuid.uuid4().hex[:8])
            super().save(*args, **kwargs)
