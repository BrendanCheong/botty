from robyn import SubRouter


router = SubRouter(__name__, prefix="")


@router.get("/health")
async def health():
    """Health check endpoint for Fly.io and monitoring."""
    return {"status": "healthy"}
