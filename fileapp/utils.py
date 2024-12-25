import os
import hashlib
import tempfile
from cryptography.fernet import Fernet
from django.conf import settings
from dotenv import load_dotenv, set_key

class FileEncryptor:
    ENV_KEY_NAME = "FERNET_KEY"
    
    @classmethod
    def initialize(cls):
        """Initialize the encryption key if it doesn't exist"""
        if not os.path.exists('.env'):
            with open('.env', 'w') as f:
                f.write('')
        load_dotenv()
        if not os.getenv(cls.ENV_KEY_NAME):
            cls.generate_key()

    @classmethod
    def generate_key(cls):
        """Generate a new Fernet key and save it to .env"""
        key = Fernet.generate_key()
        set_key(".env", cls.ENV_KEY_NAME, key.decode())
        return key

    @classmethod
    def get_key(cls):
        """Get the encryption key, generating if necessary"""
        cls.initialize()
        key = os.getenv(cls.ENV_KEY_NAME)
        if isinstance(key, str):
            key = key.encode()
        return key

    @classmethod
    def encrypt_file(cls, file_path):
        """Encrypt a file and return its hash"""
        try:
            key = cls.get_key()
            fernet = Fernet(key)
            
            # Read the original file
            with open(file_path, 'rb') as file:
                file_data = file.read()
            
            # Calculate hash of original data
            file_hash = hashlib.sha256(file_data).hexdigest()
            
            # Encrypt the data
            encrypted_data = fernet.encrypt(file_data)
            
            # Write encrypted data back to file
            with open(file_path, 'wb') as file:
                file.write(encrypted_data)
            
            return file_hash
            
        except Exception as e:
            raise Exception(f"Encryption failed: {str(e)}")

    @classmethod
    def decrypt_file(cls, file_path):
        """Decrypt a file and return the path to decrypted file and its hash"""
        try:
            key = cls.get_key()
            fernet = Fernet(key)
            
            # Read the encrypted file
            with open(file_path, 'rb') as file:
                encrypted_data = file.read()
            
            # Decrypt the data
            decrypted_data = fernet.decrypt(encrypted_data)
            
            # Get the original file extension
            _, ext = os.path.splitext(file_path)
            
            # Create a temporary file with the same extension
            temp_fd, temp_path = tempfile.mkstemp(suffix=ext)
            os.close(temp_fd)
            
            # Write decrypted data to temporary file
            with open(temp_path, 'wb') as temp_file:
                temp_file.write(decrypted_data)
            
            # Calculate hash of decrypted data
            decrypted_hash = hashlib.sha256(decrypted_data).hexdigest()
            
            return temp_path, decrypted_hash
            
        except Exception as e:
            raise Exception(f"Decryption failed: {str(e)}")