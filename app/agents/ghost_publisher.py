import jwt
import httpx
import time
from app.core.config import get_settings
from app.core.models import PublishRequest, PublishResponse
import logging

logger = logging.getLogger(__name__)

settings = get_settings()


def generate_ghost_token() -> str:
    """
    Generate a short-lived JWT token for Ghost Admin API authentication.
    Ghost uses a split key format: 'key_id:secret'
    """
    key_id, secret = settings.ghost_admin_api_key.split(":")

    # Ghost requires the secret decoded from hex
    secret_bytes = bytes.fromhex(secret)

    payload = {
        "iat": int(time.time()),           # issued at (now)
        "exp": int(time.time()) + 300,     # expires in 5 minutes
        "aud": "/admin/",                  # audience — Ghost Admin API
    }

    token = jwt.encode(
        payload,
        secret_bytes,
        algorithm="HS256",
        headers={"kid": key_id},           # key ID goes in the header
    )

    return token


def markdown_to_mobiledoc(markdown: str) -> dict:
    """
    Wrap markdown content in Ghost's Mobiledoc format.
    Ghost stores content as Mobiledoc JSON — we use the markdown card
    which tells Ghost to render it as markdown.
    """
    return {
        "version": "0.3.1",
        "markups": [],
        "atoms": [],
        "cards": [["markdown", {"markdown": markdown}]],
        "sections": [[10, 0]],
    }


async def publish_to_ghost(request: PublishRequest) -> PublishResponse:
    """
    Publish or save a draft post to Ghost CMS via the Admin API.
    """
    token = generate_ghost_token()

    headers = {
        "Authorization": f"Ghost {token}",
        "Content-Type": "application/json",
        "Accept-Version": "v5.0",
    }

    # Extract H1 title from markdown (first line starting with #)
    lines = request.markdown_content.strip().split("\n")
    title = lines[0].lstrip("# ").strip() if lines else request.topic

    # Remove the H1 line from the body — Ghost stores title separately
    body_lines = [l for l in lines if not l.startswith("# ")]
    body_markdown = "\n".join(body_lines).strip()

    mobiledoc = markdown_to_mobiledoc(body_markdown)

    post_payload = {
        "posts": [
            {
                "title": title,
                "mobiledoc": __import__("json").dumps(mobiledoc),
                "status": request.publish_status,
                "slug": request.seo_metadata.slug,
                "meta_title": request.seo_metadata.meta_title,
                "meta_description": request.seo_metadata.meta_description,
                "tags": [{"name": tag} for tag in request.tags],
            }
        ]
    }

    api_url = f"{settings.ghost_api_url.rstrip('/')}/ghost/api/admin/posts/"

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(api_url, headers=headers, json=post_payload)

        if response.status_code not in (200, 201):
            raise Exception(
                f"Ghost API error {response.status_code}: {response.text}"
            )

        data = response.json()
        post = data["posts"][0]

        logger.info(f"Post published to Ghost: {post['url']}")

        return PublishResponse(
            success=True,
            ghost_post_id=post["id"],
            ghost_post_url=post["url"],
            status=post["status"],
            title=post["title"],
        )
