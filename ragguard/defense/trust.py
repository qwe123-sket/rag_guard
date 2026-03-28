TRUSTED_AUTHORS = frozenset({
    "platform-team",
    "finance-office",
    "security-team",
})


def is_trusted_source(author: str) -> bool:
    return author in TRUSTED_AUTHORS
