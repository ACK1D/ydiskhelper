import logging
import os
import tempfile
import zipfile
from urllib.parse import quote

from django.contrib import messages
from django.http import FileResponse, HttpResponse
from django.shortcuts import redirect, render
from django.views import View

from .services import YandexDiskService

logger = logging.getLogger(__name__)


class PublicLinkView(View):
    def get(self, request):
        return render(request, "ydisk/public_link.html")

    def post(self, request):
        try:
            public_key = request.POST.get("public_key")
            media_type = request.POST.get("media_type", "")
            oauth_token = request.session.get("yandex_oauth_token")

            if not public_key:
                messages.error(request, "Public link is required")
                return render(request, "ydisk/public_link.html")

            service = YandexDiskService(public_key, oauth_token=oauth_token)

            try:
                files = service.get_files(media_type=media_type if media_type else None)
            except ValueError as ve:
                if "OAuth authorization required" in str(ve):
                    request.session["pending_public_key"] = public_key
                    return redirect("oauth_start")
                raise

            if not files:
                messages.warning(request, "No files found at the specified link")

            return render(request, "ydisk/file_list.html", {"files": files, "public_key": public_key})

        except ValueError as ve:
            messages.error(request, str(ve))
            return redirect("public_link")
        except Exception as e:
            logger.error(f"Critical error while getting files: {e}", exc_info=True)
            messages.error(request, "Failed to get file list")
            return redirect("public_link")


class MultiDownloadView(View):
    def post(self, request):
        try:
            public_key = request.POST.get("public_key")
            selected_files = request.POST.getlist("selected_files")
            oauth_token = request.session.get("yandex_oauth_token")

            if not selected_files:
                messages.error(request, "Please select files to download")
                return redirect("public_link")

            service = YandexDiskService(public_key, oauth_token=oauth_token)
            files = service.get_files()
            download_files = [f for f in files if f["name"] in selected_files]

            if len(download_files) == 1:
                file = download_files[0]
                response = service.download_file(file["path"])
                return HttpResponse(
                    response.content,
                    content_type="application/octet-stream",
                    headers={"Content-Disposition": f'attachment; filename="{quote(file["name"])}"'},
                )

            with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as temp_zip:
                with zipfile.ZipFile(temp_zip, "w") as zf:
                    for file in download_files:
                        try:
                            response = service.download_file(file["path"])
                            zf.writestr(file["name"], response.content)
                        except Exception as e:
                            logger.error(f"Error adding file {file['name']} to archive: {e}")
                            continue

                temp_zip.seek(0)
                response = FileResponse(
                    open(temp_zip.name, "rb"),
                    content_type="application/zip",
                    as_attachment=True,
                    filename="files.zip",
                )
                os.unlink(temp_zip.name)
                return response

        except Exception as e:
            logger.error(f"Critical error while downloading files: {e}", exc_info=True)
            messages.error(request, "Failed to download files")
            return redirect("public_link")
