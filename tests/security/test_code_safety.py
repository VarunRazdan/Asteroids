"""Security tests — static analysis of the codebase for dangerous patterns."""

import ast
import os

# Project root (one level above tests/)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _collect_python_files():
    """Yield all .py files in the project, excluding tests/ and venv/."""
    for dirpath, dirnames, filenames in os.walk(PROJECT_ROOT):
        # Skip test files, virtual environments, and caches
        skip = {"tests", "venv", ".venv", "__pycache__", ".git", "node_modules"}
        dirnames[:] = [d for d in dirnames if d not in skip]
        for fn in filenames:
            if fn.endswith(".py"):
                yield os.path.join(dirpath, fn)


class TestNoEvalOrExec:
    def test_no_eval_or_exec(self):
        """No production code should use eval() or exec().

        Scans the AST of every .py file for Call nodes whose function name
        is 'eval' or 'exec'.
        """
        violations = []
        for filepath in _collect_python_files():
            with open(filepath, "r", encoding="utf-8") as f:
                try:
                    tree = ast.parse(f.read(), filename=filepath)
                except SyntaxError:
                    continue  # skip files that don't parse

            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    func = node.func
                    name = None
                    if isinstance(func, ast.Name):
                        name = func.id
                    elif isinstance(func, ast.Attribute):
                        name = func.attr

                    if name in ("eval", "exec"):
                        relpath = os.path.relpath(filepath, PROJECT_ROOT)
                        violations.append(
                            f"{relpath}:{node.lineno} — {name}() call"
                        )

        assert violations == [], (
            "Found eval/exec usage in production code:\n"
            + "\n".join(violations)
        )


class TestNoHardcodedSecrets:
    # Patterns that suggest a hard-coded secret
    SECRET_PATTERNS = [
        "password", "secret", "api_key", "apikey", "token",
        "private_key", "access_key", "credentials",
    ]

    def test_no_hardcoded_secrets(self):
        """No .py file should contain string assignments that look like secrets."""
        violations = []
        for filepath in _collect_python_files():
            with open(filepath, "r", encoding="utf-8") as f:
                try:
                    tree = ast.parse(f.read(), filename=filepath)
                except SyntaxError:
                    continue

            for node in ast.walk(tree):
                # Check variable assignments like: SECRET_KEY = "abc123"
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        var_name = ""
                        if isinstance(target, ast.Name):
                            var_name = target.id.lower()
                        elif isinstance(target, ast.Attribute):
                            var_name = target.attr.lower()

                        if any(pat in var_name for pat in self.SECRET_PATTERNS):
                            # Only flag if the value is a non-empty string literal
                            if isinstance(node.value, ast.Constant) and isinstance(
                                node.value.value, str
                            ):
                                if len(node.value.value) > 0:
                                    relpath = os.path.relpath(filepath, PROJECT_ROOT)
                                    violations.append(
                                        f"{relpath}:{node.lineno} — "
                                        f"'{var_name}' assigned a string literal"
                                    )

        assert violations == [], (
            "Possible hard-coded secrets found:\n"
            + "\n".join(violations)
        )
