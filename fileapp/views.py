from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.conf import settings
from django.http import FileResponse
from django.http import JsonResponse
from django.core.exceptions import PermissionDenied

from .models import File, FileShare, ShareableLink
from .forms import FileUploadForm, UserRegistrationForm, FileShareForm
from .utils import FileEncryptor
import os
import secrets
from datetime import timedelta
from django.utils.timezone import now
from django.http import HttpResponseForbidden, FileResponse

# View for user registration
def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f"Account created for {username}!")
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'register.html', {'form': form})
    
@login_required
def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('login')

# View for generating share link

@login_required
def generate_shareable_link(request, file_id):
    """
    Generates a one-time shareable link for a file.
    """
    file = get_object_or_404(File, id=file_id)
    
    # Generate a secure token and expiration time
    token = secrets.token_urlsafe(32)
    expiration_time = now() + timedelta(hours=24)  # 24-hour validity
    
    # Create a new ShareableLink object
    shareable_link = ShareableLink.objects.create(
        file=file,
        token=token,
        expires_at=expiration_time
    )
    
    # Return the generated link
    link = f"{request.scheme}://{request.get_host()}/file/share/{shareable_link.token}/"
    return JsonResponse({'link': link})


def access_shared_file(request, token):
    """
    Validates and serves a file through a one-time shareable link.
    """
    shareable_link = get_object_or_404(ShareableLink, token=token)
    
    # Check if the link is expired or already used
    if shareable_link.has_expired() or shareable_link.is_used:
        return HttpResponseForbidden("This link is no longer valid.")
    
    # Mark the link as used
    shareable_link.is_used = True
    shareable_link.save()
    
    # Serve the file
    file = shareable_link.file
    response = FileResponse(file.file_object.open(), as_attachment=True, filename=file.file)
    return response

# View for uploading files
@login_required
def upload_file(request):
    if request.method == 'POST':
        uploaded_files = request.FILES.getlist('files')
        successful_uploads = 0
        failed_uploads = 0

        for uploaded_file in uploaded_files:
            try:
                # Create File model instance
                file = File.objects.create(
                    user=request.user,
                    filename=uploaded_file.name,
                    file=uploaded_file
                )

                # Get the full path of the saved file
                file_path = os.path.join(settings.MEDIA_ROOT, str(file.file))
                
                # Encrypt the file and get its hash
                file_hash = FileEncryptor.encrypt_file(file_path)
                file.file_hash = file_hash
                file.save()
                
                successful_uploads += 1

            except Exception as e:
                # If encryption or saving fails, delete the file
                if hasattr(locals(), 'file'):
                    file.delete()
                failed_uploads += 1
                messages.error(request, f"Failed to upload {uploaded_file.name}: {str(e)}")

        if successful_uploads > 0:
            messages.success(request, f"Successfully uploaded {successful_uploads} file(s).")
        if failed_uploads > 0:
            messages.warning(request, f"{failed_uploads} file(s) failed to upload.")
        
        return redirect('file_list')
    
    return render(request, 'upload_file.html', {'form': FileUploadForm()})

# View for listing user's files and files shared with them
@login_required
def file_list(request):
    user_files = File.objects.filter(user=request.user)
    shared_files = FileShare.objects.filter(shared_with=request.user)
    return render(request, 'file_list.html', {
        'user_files': user_files,
        'shared_files': shared_files
    })

# View for sharing a file
@login_required
def share_file(request, file_id):
    file = get_object_or_404(File, id=file_id, user=request.user)
    
    if request.method == 'POST':
        form = FileShareForm(request.POST)
        
        if form.is_valid():
            username = form.cleaned_data['username']
            
            try:
                shared_with_user = User.objects.get(username=username)
                
                # Prevent sharing with self
                if shared_with_user == request.user:
                    messages.error(request, "You cannot share a file with yourself.")
                    return redirect('file_list')
                
                # Check if file is already shared with this user
                existing_share = FileShare.objects.filter(
                    file=file, shared_with=shared_with_user
                ).exists()
                
                # Handle "Share Anyway" scenario
                if existing_share and not request.POST.get('force_share'):
                    messages.warning(request, f"This file is already shared with {shared_with_user.username}.")
                    return render(request, 'share_file.html', {
                        'form': form,
                        'file': file,
                        'existing_share': True,
                        'shared_with_username': shared_with_user.username,
                    })
                
                # Create a new share record regardless of existing shares
                FileShare.objects.create(
                    file=file,
                    shared_with=shared_with_user,
                    shared_by=request.user,
                )
                
                messages.success(request, f"File shared with {shared_with_user.username}")
                return redirect('file_list')
            
            except User.DoesNotExist:
                messages.error(request, "User not found.")
        else:
            messages.error(request, "Invalid form data.")
    else:
        form = FileShareForm()

    return render(request, 'share_file.html', {'form': form, 'file': file})

@login_required
@require_http_methods(["GET"])
def download_file(request, file_id):
    file_obj = get_object_or_404(File, id=file_id)
    
    # Check if user has permission to download
    is_owner = file_obj.user == request.user
    is_shared = FileShare.objects.filter(file=file_obj, shared_with=request.user).exists()
    
    if not (is_owner or is_shared):
        messages.error(request, "You don't have permission to download this file.")
        return redirect('file_list')
    
    try:
        file_path = os.path.join(settings.MEDIA_ROOT, str(file_obj.file))
        
        if not os.path.exists(file_path):
            messages.error(request, "File not found on the server.")
            return redirect('file_list')
        
        decrypted_path, decrypted_hash = FileEncryptor.decrypt_file(file_path)
        
        if decrypted_hash != file_obj.file_hash:
            os.unlink(decrypted_path)
            messages.error(request, "File integrity check failed.")
            return redirect('file_list')
        
        response = FileResponse(
            open(decrypted_path, 'rb'),
            as_attachment=True,
            filename=file_obj.filename
        )
        
        # Clean up the temporary file after sending
        response.close_callback = lambda: os.unlink(decrypted_path) if os.path.exists(decrypted_path) else None
        
        return response
        
    except Exception as e:
        if 'decrypted_path' in locals() and os.path.exists(decrypted_path):
            os.unlink(decrypted_path)
        messages.error(request, f"Download failed: {str(e)}")
        return redirect('file_list')
    if request.method == 'POST':  # Only allow POST requests for deletion
        file = get_object_or_404(File, id=file_id, user=request.user)
        file_path = os.path.join(settings.MEDIA_ROOT, str(file.file))
        try:
            # Delete file shares first
            FileShare.objects.filter(file=file).delete()
            
            # Delete the physical file
            if os.path.exists(file_path):
                os.remove(file_path)
            
            # Delete the database record
            file.delete()
            messages.success(request, "File deleted successfully.")
        except Exception as e:
            messages.error(request, f"Failed to delete file: {str(e)}")
    else:
        messages.error(request, "Invalid request method for file deletion.")
    
    return redirect('file_list')
    file = get_object_or_404(File, id=file_id, user=request.user)
    file_path = os.path.join(settings.MEDIA_ROOT, str(file.file))
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
        file.delete()
        messages.success(request, "File deleted successfully.")
    except Exception as e:
        messages.error(request, f"Failed to delete file: {str(e)}")
    return redirect('file_list')

@login_required
@require_http_methods(["POST"])
def delete_file(request, file_id):
    file = get_object_or_404(File, id=file_id, user=request.user)
    file_path = os.path.join(settings.MEDIA_ROOT, str(file.file))
    
    try:
        # Delete file shares first
        FileShare.objects.filter(file=file).delete()
        
        # Delete the physical file
        if os.path.exists(file_path):
            os.remove(file_path)
        
        # Delete the database record
        file.delete()
        messages.success(request, "File deleted successfully.")
    except Exception as e:
        messages.error(request, f"Failed to delete file: {str(e)}")
    
    return redirect('file_list')