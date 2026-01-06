"""GitHub Issues backend for GTD storage."""

import json
import subprocess

from ..storage import GTDItem, GTDStorage


class GitHubStorage(GTDStorage):
    """GTD storage using GitHub Issues via gh CLI."""

    def __init__(self, repo: str | None = None):
        """Initialize GitHub storage.

        Args:
            repo: Optional repo in "owner/repo" format. If not provided,
                  uses the current repo from git context.
        """
        self.repo = repo
        self._repo_args = ["--repo", repo] if repo else []

    def _run_gh(
        self, args: list[str], check: bool = True, verbose: bool = False
    ) -> str:
        """Run a gh command and return output."""
        cmd = ["gh"] + args + self._repo_args
        if verbose:
            print(f"  [DEBUG] Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            if check:
                raise RuntimeError(f"gh command failed: {result.stderr}")
            return ""
        return result.stdout

    def _get_existing_labels(self) -> set[str]:
        """Get set of existing label names in the repo."""
        labels = self._get_existing_labels_full()
        return {label["name"] for label in labels}

    def _get_existing_labels_full(self) -> list[dict]:
        """Get full label data (name, color, description) from the repo."""
        output = self._run_gh(
            ["label", "list", "--json", "name,color,description", "--limit", "200"],
            check=False,
        )
        if not output:
            return []
        try:
            return json.loads(output)
        except json.JSONDecodeError:
            return []

    # GTD label prefixes we manage
    GTD_PREFIXES = ("context/", "energy/", "status/", "horizon/")

    def get_stale_labels(self) -> list[str]:
        """Find labels with GTD prefixes that aren't in the current taxonomy.

        Returns list of label names that should be cleaned up.
        """
        existing = self._get_existing_labels()
        required = self.get_required_labels()

        stale = []
        for label in existing:
            # Only consider labels with GTD prefixes
            if any(label.startswith(prefix) for prefix in self.GTD_PREFIXES):
                if label not in required:
                    stale.append(label)
        return sorted(stale)

    def get_label_drift(self) -> list[dict]:
        """Find GTD labels with incorrect color or description.

        Returns list of dicts with: name, field, expected, actual
        """
        existing_full = self._get_existing_labels_full()
        existing_by_name = {label["name"]: label for label in existing_full}

        drift = []
        for category, items in self.LABELS.items():
            for name, config in items.items():
                label_name = f"{category}/{name}"
                if label_name in existing_by_name:
                    actual = existing_by_name[label_name]
                    # Check color (GitHub returns without #, lowercase)
                    expected_color = config["color"].lower()
                    actual_color = actual.get("color", "").lower()
                    if expected_color != actual_color:
                        drift.append(
                            {
                                "name": label_name,
                                "field": "color",
                                "expected": expected_color,
                                "actual": actual_color,
                            }
                        )
                    # Check description
                    expected_desc = config["description"]
                    actual_desc = actual.get("description", "")
                    if expected_desc != actual_desc:
                        drift.append(
                            {
                                "name": label_name,
                                "field": "description",
                                "expected": expected_desc,
                                "actual": actual_desc,
                            }
                        )
        return drift

    def delete_label(self, name: str) -> bool:
        """Delete a label by name.

        Returns True if deleted, False if failed.
        """
        try:
            self._run_gh(["label", "delete", name, "--yes"])
            return True
        except RuntimeError:
            return False

    def fix_label(self, name: str, color: str, description: str) -> bool:
        """Fix a label's color and description.

        Returns True if fixed, False if failed.
        """
        try:
            self._run_gh(
                [
                    "label",
                    "edit",
                    name,
                    "--color",
                    color,
                    "--description",
                    description,
                ]
            )
            return True
        except RuntimeError:
            return False

    def is_setup(self) -> bool:
        """Check if GTD labels exist in the repo."""
        existing = self._get_existing_labels()
        required = self.get_required_labels()
        return required.issubset(existing)

    def setup(self, verbose: bool = False) -> None:
        """Create all GTD labels in the repo."""
        existing = self._get_existing_labels()

        created = 0
        skipped = 0

        for category, items in self.LABELS.items():
            if verbose:
                print(f"→ {category.capitalize()} labels...")

            for name, config in items.items():
                label_name = f"{category}/{name}"

                if label_name in existing:
                    skipped += 1
                    continue

                try:
                    self._run_gh(
                        [
                            "label",
                            "create",
                            label_name,
                            "--color",
                            config["color"],
                            "--description",
                            config["description"],
                            "--force",
                        ]
                    )
                    created += 1
                except RuntimeError as e:
                    if verbose:
                        print(f"  Warning: Could not create {label_name}: {e}")

        if verbose:
            print(
                f"✓ Setup complete: {created} labels created, {skipped} already existed"
            )
            print(f"  Total GTD labels: {len(self.get_all_labels())}")

    def _parse_issue(self, data: dict) -> GTDItem:
        """Parse gh JSON output into GTDItem.

        Maps GitHub's 'milestone' to GTD's 'project' concept.
        """
        labels = [label["name"] for label in data.get("labels", [])]
        milestone = data.get("milestone", {})
        return GTDItem(
            id=str(data["number"]),
            title=data["title"],
            body=data.get("body"),
            state=data.get("state", "open").lower(),
            labels=labels,
            project=milestone.get("title")
            if milestone
            else None,  # milestone → project
            url=data.get("url"),
            created_at=data.get("createdAt"),
            closed_at=data.get("closedAt"),
        )

    def create_item(
        self,
        title: str,
        labels: list[str],
        body: str | None = None,
        project: str | None = None,
    ) -> GTDItem:
        """Create a new issue.

        Args:
            project: GTD project name (mapped to GitHub milestone)
        """
        args = ["issue", "create", "--title", title]

        if labels:
            args.extend(["--label", ",".join(labels)])
        if body:
            args.extend(["--body", body])
        if project:
            args.extend(["--milestone", project])  # project → milestone

        # Get the created issue URL
        output = self._run_gh(args)
        # Output is the issue URL
        issue_url = output.strip()

        # Extract issue number from URL and fetch full details
        issue_number = issue_url.split("/")[-1]
        return self.get_item(issue_number)

    def get_item(self, item_id: str) -> GTDItem | None:
        """Get a single issue by number."""
        args = [
            "issue",
            "view",
            item_id,
            "--json",
            "number,title,body,state,labels,milestone,url,createdAt,closedAt",
        ]
        try:
            output = self._run_gh(args)
            data = json.loads(output)
            return self._parse_issue(data)
        except (RuntimeError, json.JSONDecodeError):
            return None

    def list_items(
        self,
        labels: list[str] | None = None,
        state: str = "open",
        project: str | None = None,
        limit: int = 100,
        verbose: bool = False,
    ) -> list[GTDItem]:
        """List issues matching criteria.

        Args:
            project: Filter by GTD project (mapped to GitHub milestone)
        """
        args = [
            "issue",
            "list",
            "--state",
            state,
            "--limit",
            str(limit),
            "--json",
            "number,title,body,state,labels,milestone,url,createdAt,closedAt",
        ]

        if labels:
            args.extend(["--label", ",".join(labels)])
        if project:
            args.extend(["--milestone", project])  # project → milestone

        output = self._run_gh(args, verbose=verbose)
        data = json.loads(output)

        if verbose:
            print(f"  [DEBUG] Got {len(data)} items from GitHub")

        return [self._parse_issue(item) for item in data]

    def update_item(
        self,
        item_id: str,
        title: str | None = None,
        body: str | None = None,
        labels: list[str] | None = None,
        project: str | None = None,
    ) -> GTDItem:
        """Update an existing issue.

        Args:
            project: GTD project name (mapped to GitHub milestone)
        """
        args = ["issue", "edit", item_id]

        if title:
            args.extend(["--title", title])
        if body:
            args.extend(["--body", body])
        if project:
            args.extend(["--milestone", project])  # project → milestone

        # For labels, we need to get current labels first if doing partial update
        if labels is not None:
            # Clear existing labels and set new ones
            # gh issue edit doesn't have --label-clear, so we remove then add
            current = self.get_item(item_id)
            if current:
                for label in current.labels:
                    self._run_gh(
                        ["issue", "edit", item_id, "--remove-label", label], check=False
                    )
            for label in labels:
                self._run_gh(["issue", "edit", item_id, "--add-label", label])

        if title or body or project:
            self._run_gh(args)

        return self.get_item(item_id)

    def add_labels(self, item_id: str, labels: list[str]) -> GTDItem:
        """Add labels to an issue."""
        for label in labels:
            self._run_gh(["issue", "edit", item_id, "--add-label", label])
        return self.get_item(item_id)

    def remove_labels(self, item_id: str, labels: list[str]) -> GTDItem:
        """Remove labels from an issue."""
        for label in labels:
            self._run_gh(
                ["issue", "edit", item_id, "--remove-label", label], check=False
            )
        return self.get_item(item_id)

    def close_item(self, item_id: str) -> GTDItem:
        """Close an issue."""
        self._run_gh(["issue", "close", item_id])
        return self.get_item(item_id)

    def reopen_item(self, item_id: str) -> GTDItem:
        """Reopen a closed issue."""
        self._run_gh(["issue", "reopen", item_id])
        return self.get_item(item_id)

    # Milestone management for project support

    def list_milestones(self, state: str = "open") -> list[dict]:
        """List all milestones with progress information.

        Returns list of dicts with: title, description, due_on, open_issues,
        closed_issues, state, url
        """
        output = self._run_gh(
            [
                "api",
                f"repos/:owner/:repo/milestones?state={state}",
                "--jq",
                ".[] | {number, title, description, due_on, "
                "open_issues, closed_issues, state, url}",
            ],
            check=False,
        )

        if not output:
            return []

        milestones = []
        for line in output.strip().split("\n"):
            if line:
                try:
                    milestones.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
        return milestones

    def get_milestone(self, title: str) -> dict | None:
        """Get a milestone by title."""
        milestones = self.list_milestones(state="all")
        for m in milestones:
            if m.get("title") == title:
                return m
        return None

    def create_milestone(
        self,
        title: str,
        description: str | None = None,
        due_on: str | None = None,
    ) -> dict:
        """Create a new milestone.

        Args:
            title: Milestone title
            description: Optional description
            due_on: Optional due date in ISO 8601 format (YYYY-MM-DDTHH:MM:SSZ)

        Returns:
            Created milestone data
        """
        # Check if milestone already exists
        existing = self.get_milestone(title)
        if existing:
            return existing

        # Build the API request
        args = [
            "api",
            "repos/:owner/:repo/milestones",
            "-X",
            "POST",
            "-f",
            f"title={title}",
        ]
        if description:
            args.extend(["-f", f"description={description}"])
        if due_on:
            args.extend(["-f", f"due_on={due_on}"])

        output = self._run_gh(args)
        return json.loads(output)

    def ensure_project(self, name: str) -> dict:
        """Ensure a project exists, creating it if needed.

        In GitHub, projects are implemented as milestones.
        """
        existing = self.get_milestone(name)
        if existing:
            return existing
        return self.create_milestone(name)

    def update_milestone(
        self,
        title: str,
        *,
        description: str | None = None,
        due_on: str | None = None,
        state: str | None = None,
    ) -> dict | None:
        """Update an existing milestone.

        Args:
            title: Milestone title to find
            description: New description (optional)
            due_on: New due date in ISO 8601 format (optional)
            state: New state - "open" or "closed" (optional)

        Returns:
            Updated milestone data, or None if not found
        """
        milestone = self.get_milestone(title)
        if not milestone:
            return None

        number = milestone.get("number")
        if not number:
            return None

        args = ["api", f"repos/:owner/:repo/milestones/{number}", "-X", "PATCH"]
        if description is not None:
            args.extend(["-f", f"description={description}"])
        if due_on is not None:
            args.extend(["-f", f"due_on={due_on}"])
        if state is not None:
            args.extend(["-f", f"state={state}"])

        output = self._run_gh(args)
        return json.loads(output)

    def delete_milestone(self, title: str) -> bool:
        """Delete a milestone by title.

        Args:
            title: Milestone title to delete

        Returns:
            True if deleted, False if not found
        """
        milestone = self.get_milestone(title)
        if not milestone:
            return False

        number = milestone.get("number")
        if not number:
            return False

        self._run_gh(["api", f"repos/:owner/:repo/milestones/{number}", "-X", "DELETE"])
        return True
