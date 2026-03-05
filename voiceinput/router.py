import re


class Router:
    def __init__(self, instances: dict[str, str]):
        self._instances = instances
        if instances:
            # Build pattern like: ^in (?:the )?(p210|backend|frontend)[\s,:]*
            names = sorted(instances.keys(), key=len, reverse=True)
            escaped = [re.escape(n) for n in names]
            self._pattern = re.compile(
                r"^in\s+(?:the\s+)?(" + "|".join(escaped) + r")(?:\s+instance)?[\s,:.]*",
                re.IGNORECASE,
            )
        else:
            self._pattern = None

    def route(self, text: str) -> tuple[str, str]:
        """Returns (target, cleaned_text). Target is empty string if no match."""
        if not self._pattern:
            return "", text

        m = self._pattern.match(text)
        if not m:
            return "", text

        name = m.group(1).lower()
        target = self._instances.get(name, "")
        cleaned = text[m.end():].strip()
        # Don't route if there's no actual text left
        if not cleaned:
            return "", text
        return target, cleaned
