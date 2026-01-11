from github import Github
from config.github_config import GitHubConfig

class GitHubClient:
    def __init__(self):
        GitHubConfig.validate()
        self.client = Github(GitHubConfig.TOKEN)
        self.repo = self.client.get_repo(f"{GitHubConfig.OWNER}/{GitHubConfig.REPO}")
        self.base_branch = GitHubConfig.BASE_BRANCH

    def get_file(self, path: str, ref="main"):
        try:
            return self.repo.get_contents(path, ref=ref)
        except Exception:
            return None

    def create_branch(self, branch: str, base="main"):
        base_ref = self.repo.get_git_ref(f"heads/{base}")
        self.repo.create_git_ref(
            ref=f"refs/heads/{branch}",
            sha=base_ref.object.sha
        )

    def commit_file(
        self, path: str, content: str, message: str, branch: str
    ):
        existing = self.get_file(path, ref=branch)
        if existing:
            self.repo.update_file(
                path, message, content, existing.sha, branch
            )
        else:
            self.repo.create_file(
                path, message, content, branch
            )

    def create_pr(self, branch: str, title: str, body: str):
        return self.repo.create_pull(
            title=title,
            body=body,
            head=branch,
            base="main"
        )
