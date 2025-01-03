import logging
from urllib.parse import urlencode

import requests
from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect


def yandex_oauth_start(request):
    """
    Redirect user to Yandex OAuth authorization page
    """
    params = {
        "response_type": "code",
        "client_id": settings.YANDEX_OAUTH_CONFIG["CLIENT_ID"],
        "redirect_uri": settings.YANDEX_OAUTH_CONFIG["REDIRECT_URI"],
        "scope": " ".join(settings.YANDEX_OAUTH_CONFIG["SCOPES"]),
    }
    authorize_url = f"{settings.YANDEX_OAUTH_CONFIG['AUTHORIZE_URL']}?{urlencode(params)}"
    return redirect(authorize_url)


def yandex_oauth_callback(request):
    """
    Handle OAuth callback after authorization
    """
    code = request.GET.get("code")

    if not code:
        messages.error(request, "Authorization code not received")
        return redirect("public_link")

    try:
        token_response = requests.post(
            "https://oauth.yandex.ru/token",
            data={
                "grant_type": "authorization_code",
                "code": code,
                "client_id": settings.YANDEX_OAUTH_CONFIG["CLIENT_ID"],
                "client_secret": settings.YANDEX_OAUTH_CONFIG["CLIENT_SECRET"],
            },
            timeout=10,
        )
        token_response.raise_for_status()
        token_data = token_response.json()

        request.session["yandex_oauth_token"] = token_data["access_token"]

        if "pending_public_key" in request.session:
            public_key = request.session.pop("pending_public_key")
            messages.success(request, "Authorization successful")
            return redirect("public_link") + f"?public_key={public_key}"

        return redirect("public_link")

    except requests.RequestException as e:
        logging.error(f"OAuth error: {e}")
        messages.error(request, "Authorization failed. Please try again.")
        return redirect("public_link")
