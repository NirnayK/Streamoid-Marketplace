import re

from rest_framework import serializers

from core.constants import KEY_SPLIT_PATTERN, KEY_TOKEN_PATTERN


class ValidationHelpers:
    """Utility helpers for normalizing keys and validating values."""

    @classmethod
    def evaluate_boolean(cls, value, default):
        """Return a validated boolean value or fall back to default."""
        field = serializers.BooleanField()
        try:
            return field.run_validation(value)
        except (serializers.ValidationError, TypeError, ValueError):
            return default

    @classmethod
    def _split_key_tokens(cls, value):
        """Split a string into lowercase tokens for key normalization."""
        if value is None:
            return []

        parts = re.split(KEY_SPLIT_PATTERN, str(value).strip())
        tokens = []
        for part in parts:
            if not part:
                continue
            tokens.extend(re.findall(KEY_TOKEN_PATTERN, part))
        return [token.lower() for token in tokens if token]

    @classmethod
    def key_variants(cls, *parts, include_short=True):
        """Build common key variants (snake, camel, compact, optional short)."""
        tokens = []
        for part in parts:
            tokens.extend(cls._split_key_tokens(part))
        if not tokens:
            return set()

        snake = "_".join(tokens)
        camel = tokens[0] + "".join(token.title() for token in tokens[1:])
        compact = "".join(tokens)

        variants = {snake, camel, compact}
        if include_short and len(tokens) > 1:
            variants.add(tokens[0])
        return variants

    @classmethod
    def get_variant_value(cls, mapping, *parts, default=None, include_short=True):
        """Return the first matching variant value from a mapping."""
        for key in cls.key_variants(*parts, include_short=include_short):
            if key in mapping:
                return mapping[key]
        return default
