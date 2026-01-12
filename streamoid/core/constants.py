PRODUCTION = "production"
LOCAL = "local"
MAX_NAME_LENGTH = 255
HEAD_DATA = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Credentials": "true",
    "Access-Control-Allow-Headers": "X-Requested-With, Content-Type, Set-Cookie",
    "content_type": "application/json",
}

# Tokenizes strings into words, supporting camel case and acronyms.
KEY_TOKEN_PATTERN = r"[A-Z]?[a-z0-9]+|[A-Z]+(?![a-z])"
# Splits on whitespace, underscores, and hyphens.
KEY_SPLIT_PATTERN = r"[\s_-]+"
