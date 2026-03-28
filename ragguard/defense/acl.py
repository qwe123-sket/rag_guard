from ragguard.models import RetrievalHit


ACCESS_MAP = {
    "ops": {"public", "internal"},
    "finance": {"public", "internal", "confidential"},
    "hr": {"public", "internal", "confidential"},
}


def allowed_classifications(user_dept: str) -> set[str]:
    return ACCESS_MAP.get(user_dept, {"public"})


def acl_filter(hits: list[RetrievalHit], user_dept: str) -> tuple[list[RetrievalHit], list[RetrievalHit]]:
    allowed_cls = allowed_classifications(user_dept)
    visible: list[RetrievalHit] = []
    denied: list[RetrievalHit] = []

    for hit in hits:
        if hit.department == "external":
            denied.append(hit)
        elif hit.classification not in allowed_cls:
            denied.append(hit)
        elif hit.department not in (user_dept, "shared"):
            denied.append(hit)
        else:
            visible.append(hit)

    return visible, denied
