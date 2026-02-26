def normalize_history_role(role: str) -> str:
    """
    Normalize persisted roles to internal provider-neutral roles.
    DB uses: user/assistant. Legacy payloads may contain: model/maisu/system.
    """
    role_l = (role or "").strip().lower()
    if role_l in ("assistant", "model", "maisu"):
        return "model"
    if role_l == "system":
        return "system"
    return "user"
