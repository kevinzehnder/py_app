import uvicorn

from app.core.bootstrap import bootstrap


def main() -> None:
    settings = bootstrap()
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.ENVIRONMENT == "dev",
        log_config=None,
        access_log=False,
    )


if __name__ == "__main__":
    main()
