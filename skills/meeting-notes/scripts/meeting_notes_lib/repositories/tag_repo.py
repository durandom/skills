"""
Tag Repository - Query and mutate tag definition records.
"""

from ..db import MeetingNotesDB
from ..models import Tag


class TagRepository:
    """Repository for tag definitions.

    Tags categorize meetings (e.g., 'rhdh', 'one-on-ones', 'team').
    This repository provides CRUD operations for tag definitions
    with optional metadata like description and color.
    """

    def __init__(self, db: MeetingNotesDB):
        self.db = db

    # --- Query Operations ---

    def get(self, name: str) -> Tag | None:
        """Get tag definition by name.

        Args:
            name: Tag name

        Returns:
            Tag object or None if not found
        """
        record = self.db.get_tag(name)
        if record is None:
            return None
        return Tag.from_dict(record.get("data", {}))

    def get_all(self) -> list[Tag]:
        """Get all tag definitions.

        Returns:
            List of Tag objects
        """
        records = self.db.get_all_tags()
        return [Tag.from_dict(r.get("data", {})) for r in records.values()]

    def get_all_dict(self) -> dict[str, Tag]:
        """Get all tags as dict keyed by name.

        Returns:
            Dict mapping tag name to Tag object
        """
        return {tag.name: tag for tag in self.get_all()}

    def exists(self, name: str) -> bool:
        """Check if a tag exists.

        Args:
            name: Tag name

        Returns:
            True if tag exists
        """
        return self.db.get_tag(name) is not None

    def count(self) -> int:
        """Get total number of tags.

        Returns:
            Tag count
        """
        return len(self.db.get_all_tags())

    # --- Mutation Operations ---

    def create(
        self,
        name: str,
        description: str = "",
        color: str | None = None,
    ) -> Tag:
        """Create a new tag.

        Args:
            name: Tag name (must be unique)
            description: Human-readable description
            color: Optional hex color (e.g., "#e63946")

        Returns:
            Created Tag object

        Raises:
            ValueError: If tag already exists
        """
        if self.exists(name):
            raise ValueError(f"Tag '{name}' already exists")

        data = {
            "name": name,
            "description": description,
            "color": color,
        }
        self.db.upsert_tag(name, data)
        return self.get(name)

    def update(
        self,
        name: str,
        description: str | None = None,
        color: str | None = None,
    ) -> Tag | None:
        """Update an existing tag.

        Args:
            name: Tag name
            description: New description (or None to keep existing)
            color: New color (or None to keep existing)

        Returns:
            Updated Tag object, or None if tag not found
        """
        tag = self.get(name)
        if tag is None:
            return None

        if description is not None:
            tag.description = description
        if color is not None:
            tag.color = color

        self.db.upsert_tag(name, tag.to_dict())
        return self.get(name)

    def upsert(self, tag: Tag) -> str:
        """Insert or update a tag.

        Args:
            tag: Tag object to save

        Returns:
            Record ID
        """
        return self.db.upsert_tag(tag.name, tag.to_dict())

    def delete(self, name: str) -> bool:
        """Delete a tag.

        Args:
            name: Tag name

        Returns:
            True if tag was deleted, False if not found
        """
        if not self.exists(name):
            return False

        self.db.delete_tag(name)
        return True

    def rename(self, old_name: str, new_name: str) -> Tag | None:
        """Rename a tag.

        Args:
            old_name: Current tag name
            new_name: New tag name

        Returns:
            Renamed Tag object, or None if old tag not found

        Raises:
            ValueError: If new_name already exists
        """
        if not self.exists(old_name):
            return None

        if self.exists(new_name):
            raise ValueError(f"Tag '{new_name}' already exists")

        self.db.rename_tag(old_name, new_name)
        return self.get(new_name)

    # --- Utility Operations ---

    def get_or_create(
        self,
        name: str,
        description: str = "",
        color: str | None = None,
    ) -> Tag:
        """Get existing tag or create if not exists.

        Args:
            name: Tag name
            description: Description (only used if creating)
            color: Color (only used if creating)

        Returns:
            Tag object (existing or newly created)
        """
        tag = self.get(name)
        if tag is not None:
            return tag
        return self.create(name, description, color)

    def ensure_tags_exist(self, names: list[str]) -> list[Tag]:
        """Ensure all tags in list exist, creating any missing ones.

        Args:
            names: List of tag names

        Returns:
            List of Tag objects (in same order as input)
        """
        result = []
        for name in names:
            tag = self.get_or_create(name)
            result.append(tag)
        return result

    def list_names(self) -> list[str]:
        """Get list of all tag names.

        Returns:
            Sorted list of tag names
        """
        return sorted(self.get_all_dict().keys())
