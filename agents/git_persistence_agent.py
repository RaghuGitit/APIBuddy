from infra.git.github_client import GitHubClient
import json
from datetime import datetime

class GitPersistenceAgent:

    def __init__(self, github_client: GitHubClient):
        self.git = github_client

    def persist(
        self,
        api_name: str,
        version: str,
        openapi_spec: dict | None,
        schemas: dict | None,
        change_summary: str
    ) -> dict:

        branch = f"apibuddy/{api_name}/{version}-{int(datetime.utcnow().timestamp())}"
        self.git.create_branch(branch)

        if openapi_spec:
            self.git.commit_file(
                path=f"apis/{api_name}/{version}/openapi.yaml",
                content=json.dumps(openapi_spec, indent=2),
                message=f"Update OpenAPI spec for {api_name} {version}",
                branch=branch
            )

        if schemas:
            for name, schema in schemas.items():
                self.git.commit_file(
                    path=f"schemas/{api_name}/{version}/{name}.json",
                    content=json.dumps(schema, indent=2),
                    message=f"Update schema {name}",
                    branch=branch
                )

        pr = self.git.create_pr(
            branch=branch,
            title=f"[APIBuddy] {api_name} {version}",
            body=change_summary
        )

        return {
            "branch": branch,
            "pr_url": pr.html_url
        }
