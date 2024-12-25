from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

from django.contrib.auth.models import AbstractUser, Group

class UserRole(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('user', 'User'),
        ('guest', 'Guest'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=50, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.user.username} - {self.role}"


# Model representing a file uploaded by a user
class File(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE
    )  # ForeignKey relationship to the User model; if the user is deleted, their files are also deleted
    file = models.FileField(
        upload_to='encrypted_files/'
    )  # FileField to store the uploaded file; files are saved in the 'encrypted_files/' directory
    filename = models.CharField(
        max_length=255
    )  # Stores the name of the file as a string with a max length of 255 characters
    upload_date = models.DateTimeField(
        default=timezone.now
    )  # Timestamp for when the file was uploaded, defaults to the current time
    file_hash = models.CharField(
        max_length=64
    )  # Stores the SHA-256 hash of the file for integrity or encryption purposes
    is_encrypted = models.BooleanField(
        default=True
    )  # Boolean to indicate whether the file is encrypted

    def __str__(self):
        
        return self.filename

# Model representing the sharing of a file between users
class FileShare(models.Model):
    file = models.ForeignKey(
        File, on_delete=models.CASCADE
    )  # ForeignKey relationship to the File model; if the file is deleted, the share record is also deleted
    shared_by = models.ForeignKey(
        User, related_name='shared_files', on_delete=models.CASCADE
    )  # User who shares the file
    shared_with = models.ForeignKey(
        User, related_name='received_files', on_delete=models.CASCADE
    )  # User with whom the file is shared
    permission = models.CharField(
        max_length=10, choices=[('view', 'View'), ('download', 'Download')]
    )  # Permission level for the shared file
    shared_date = models.DateTimeField(
        default=timezone.now
    )  # Timestamp for when the file was shared, defaults to the current time
    expiration_date = models.DateTimeField(null=True, blank=True)

    def is_expired(self):
        return timezone.now() > self.expiration_date
    
    def __str__(self):
        
        return f"{self.file.filename} shared with {self.shared_with.username}"
    
class ShareableLink(models.Model):
    file = models.ForeignKey(File, on_delete=models.CASCADE)
    token = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    
    def has_expired(self):
        return self.expires_at < timezone.now()
    def __str__(self):
        return f"Link for {self.file.filename} shared by {self.shared_by.username}"