"""Tests for GTD metadata parsing and serialization."""

from datetime import date

from gtdlib.metadata import (
    GTDMetadata,
    is_deferred,
    is_due_before,
    is_overdue,
    parse_metadata,
    update_body_metadata,
)


class TestGTDMetadataDataclass:
    """Test GTDMetadata serialization methods."""

    def test_empty_metadata_is_empty(self):
        m = GTDMetadata()
        assert m.is_empty() is True

    def test_metadata_with_due_is_not_empty(self):
        m = GTDMetadata(due=date(2026, 3, 1))
        assert m.is_empty() is False

    def test_to_dict_excludes_none_fields(self):
        m = GTDMetadata(due=date(2026, 3, 1))
        d = m.to_dict()
        assert d == {"due": "2026-03-01"}
        assert "defer_until" not in d
        assert "waiting_for" not in d
        assert "blocked_by" not in d

    def test_to_dict_all_fields(self):
        m = GTDMetadata(
            due=date(2026, 3, 1),
            defer_until=date(2026, 2, 15),
            waiting_for={"person": "Alice", "reason": "review"},
            blocked_by=[42, 43],
        )
        d = m.to_dict()
        assert d["due"] == "2026-03-01"
        assert d["defer_until"] == "2026-02-15"
        assert d["waiting_for"] == {"person": "Alice", "reason": "review"}
        assert d["blocked_by"] == [42, 43]

    def test_to_comment_produces_html_comment(self):
        m = GTDMetadata(due=date(2026, 3, 1))
        comment = m.to_comment()
        assert comment.startswith("<!-- gtd-metadata:")
        assert comment.endswith("-->")
        assert '"due":"2026-03-01"' in comment


class TestParseMetadata:
    """Test parsing metadata from issue body text."""

    def test_parse_none_body(self):
        m = parse_metadata(None)
        assert m.is_empty()

    def test_parse_empty_body(self):
        m = parse_metadata("")
        assert m.is_empty()

    def test_parse_body_without_metadata(self):
        m = parse_metadata("Just a regular issue body.")
        assert m.is_empty()

    def test_parse_due_date(self):
        body = '<!-- gtd-metadata: {"due":"2026-03-01"} -->'
        m = parse_metadata(body)
        assert m.due == date(2026, 3, 1)

    def test_parse_all_fields(self):
        body = (
            "<!-- gtd-metadata: "
            '{"due":"2026-03-01","defer_until":"2026-02-15",'
            '"waiting_for":{"person":"Alice"},"blocked_by":[42]}'
            " -->"
        )
        m = parse_metadata(body)
        assert m.due == date(2026, 3, 1)
        assert m.defer_until == date(2026, 2, 15)
        assert m.waiting_for == {"person": "Alice"}
        assert m.blocked_by == [42]

    def test_parse_metadata_surrounded_by_text(self):
        body = (
            "Some text before\n"
            '<!-- gtd-metadata: {"due":"2026-03-01"} -->\n'
            "Some text after"
        )
        m = parse_metadata(body)
        assert m.due == date(2026, 3, 1)

    def test_parse_malformed_json_returns_empty(self):
        body = "<!-- gtd-metadata: {not valid json} -->"
        m = parse_metadata(body)
        assert m.is_empty()

    def test_roundtrip_through_comment(self):
        original = GTDMetadata(
            due=date(2026, 3, 1),
            waiting_for={"person": "Bob", "reason": "approval"},
            blocked_by=[10, 20],
        )
        comment = original.to_comment()
        parsed = parse_metadata(comment)
        assert parsed.due == original.due
        assert parsed.waiting_for == original.waiting_for
        assert parsed.blocked_by == original.blocked_by


class TestUpdateBodyMetadata:
    """Test inserting/replacing metadata in body text."""

    def test_insert_into_empty_body(self):
        m = GTDMetadata(due=date(2026, 3, 1))
        result = update_body_metadata(None, m)
        assert "<!-- gtd-metadata:" in result

    def test_insert_before_existing_text(self):
        m = GTDMetadata(due=date(2026, 3, 1))
        result = update_body_metadata("Existing body text", m)
        assert result.startswith("<!-- gtd-metadata:")
        assert "Existing body text" in result

    def test_replace_existing_metadata(self):
        old_body = '<!-- gtd-metadata: {"due":"2026-01-01"} -->\n\nBody'
        new_meta = GTDMetadata(due=date(2026, 6, 15))
        result = update_body_metadata(old_body, new_meta)
        assert "2026-06-15" in result
        assert "2026-01-01" not in result
        assert "Body" in result

    def test_empty_metadata_removes_comment(self):
        body = '<!-- gtd-metadata: {"due":"2026-01-01"} -->\n\nBody text'
        result = update_body_metadata(body, GTDMetadata())
        assert "gtd-metadata" not in result
        assert "Body text" in result


class TestMetadataPredicates:
    """Test is_deferred, is_overdue, is_due_before."""

    def test_not_deferred_when_no_defer(self):
        assert is_deferred(GTDMetadata()) is False

    def test_not_deferred_when_past(self):
        m = GTDMetadata(defer_until=date(2020, 1, 1))
        assert is_deferred(m) is False

    def test_deferred_when_future(self):
        m = GTDMetadata(defer_until=date(2099, 12, 31))
        assert is_deferred(m) is True

    def test_not_overdue_when_no_due(self):
        assert is_overdue(GTDMetadata()) is False

    def test_overdue_when_past(self):
        m = GTDMetadata(due=date(2020, 1, 1))
        assert is_overdue(m) is True

    def test_not_overdue_when_future(self):
        m = GTDMetadata(due=date(2099, 12, 31))
        assert is_overdue(m) is False

    def test_due_before_target(self):
        m = GTDMetadata(due=date(2026, 3, 1))
        assert is_due_before(m, date(2026, 3, 15)) is True

    def test_due_on_target(self):
        m = GTDMetadata(due=date(2026, 3, 1))
        assert is_due_before(m, date(2026, 3, 1)) is True

    def test_not_due_before_target(self):
        m = GTDMetadata(due=date(2026, 3, 15))
        assert is_due_before(m, date(2026, 3, 1)) is False

    def test_due_before_returns_false_when_no_due(self):
        assert is_due_before(GTDMetadata(), date(2026, 3, 1)) is False
