from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from .models import File

# Form for user login
class LoginForm(forms.Form):
    username = forms.CharField(max_length=150)  # Field for username input
    password = forms.CharField(widget=forms.PasswordInput)  # Field for password input with masked characters

# Form for file upload
class FileUploadForm(forms.Form):
    files = forms.FileField(
        widget=forms.FileInput(),  # Widget to render file input field
        validators=[FileExtensionValidator(
            allowed_extensions=['txt', 'pdf', 'docx', 'jpg', 'png', 'zip']  # Restrict allowed file types
        )],
        help_text="Allowed file types: txt, pdf, docx, jpg, png, zip"  # Help text displayed in the form
    )

    def clean_files(self):
        """
        Custom validation for files.
        Ensures all uploaded files meet specified conditions.
        """
        files = self.files.getlist('files')  # Retrieve list of uploaded files
        cleaned_files = []
        for file in files:
            # Additional file validation can be added here (e.g., size, content type)
            cleaned_files.append(file)
        return cleaned_files

    class Meta:
        model = File  # Specify the model associated with this form
        fields = ['file']  # Specify fields to include from the File model

# Form for user registration, extending Django's UserCreationForm
class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField()  # Field for email input

    class Meta:
        model = User  # Specify the User model for this form
        fields = ['username', 'email', 'password1', 'password2']  # Fields to be displayed in the form

# Form for sharing a file with another user
class FileShareForm(forms.Form):
    username = forms.CharField(
        max_length=150,  # Maximum length for the username
        help_text="Enter the username to share with"  # Help text to guide the user
    )
