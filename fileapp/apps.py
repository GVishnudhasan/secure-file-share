from django.apps import AppConfig

# Define the configuration for the 'fileapp' application
class FileappConfig(AppConfig):

    # Specify the type of auto-generated primary key fields for models
    default_auto_field = "django.db.models.BigAutoField"
    
    # Set the name of the application
    name = "fileapp"
