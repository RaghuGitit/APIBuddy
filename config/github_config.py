import os

class GitHubConfig:
    TOKEN = os.getenv("GITHUB_TOKEN")
    OWNER = os.getenv("GITHUB_OWNER")
    REPO = os.getenv("GITHUB_REPO")
    BASE_BRANCH = os.getenv("GITHUB_BASE_BRANCH", "main")

    @classmethod
    def validate(cls):
        missing = []
        for key in ["TOKEN", "OWNER", "REPO"]:
            if not getattr(cls, key):
                missing.append(key)
        if missing:
            raise RuntimeError(
                f"Missing GitHub configuration: {missing}"
            )
