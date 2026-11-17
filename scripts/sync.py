#!/usr/bin/env python3
"""Copy the team skills from dev-skills into a project repository, or report drift.

    sync.py check <repo>            report which team skills are missing or differ
    sync.py pr <repo> [--dry-run]   copy them on a new branch and open a pull request

Skills are written as real files to `<repo>/.agents/skills/<name>/`, which pi and
other Agent Skills tools read. Claude Code reads `<repo>/.claude/skills/`; when that
folder does not exist it becomes a symlink to `../.agents/skills`, the layout
CompleteFlight already uses. A repo whose `.claude/skills` is a real folder gets a
copy there too.

Each synced skill carries `.dev-skills.json` with the source commit, so `check` can
say what changed since the last sync. Edit the skills in dev-skills, not in the repo;
the next sync overwrites repo edits.
"""

import argparse
import filecmp
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "skills"
# Team skills: the standards that improve code before it reaches review.
TEAM = [
    "tests",
    "smells",
    "principle-fix-root-causes",
    "principle-separate-before-serializing-shared-state",
    "principle-make-operations-idempotent",
]
MARKER = ".dev-skills.json"


def run(*cmd, cwd=None, check=True):
    return subprocess.run(cmd, cwd=cwd, check=check, capture_output=True, text=True).stdout.strip()


def tree_hash(folder: Path) -> str:
    digest = hashlib.sha256()
    for f in sorted(p for p in folder.rglob("*") if p.is_file() and p.name != MARKER):
        digest.update(str(f.relative_to(folder)).encode())
        digest.update(f.read_bytes())
    return digest.hexdigest()


def targets(repo: Path) -> list[Path]:
    """Skill folders to write into; a symlinked .claude/skills shares .agents/skills."""
    agents = repo / ".agents/skills"
    claude = repo / ".claude/skills"
    found = [agents]
    if claude.exists() and not claude.is_symlink():
        found.append(claude)
    return found


def check(repo: Path) -> list[str]:
    source_commit = run("git", "rev-parse", "--short", "HEAD", cwd=ROOT)
    report = []
    for name in TEAM:
        want = tree_hash(SKILLS / name)
        for base in targets(repo):
            dest = base / name
            rel = dest.relative_to(repo)
            if not dest.exists():
                report.append(f"missing  {rel}")
            elif tree_hash(dest) != want:
                marker = dest / MARKER
                synced = json.loads(marker.read_text())["commit"] if marker.exists() else "unknown"
                report.append(f"differs  {rel} (synced from {synced}, dev-skills is at {source_commit})")
    if not (repo / ".claude/skills").exists():
        report.append("missing  .claude/skills (will link to ../.agents/skills)")
    return report


def copy_skills(repo: Path) -> None:
    commit = run("git", "rev-parse", "HEAD", cwd=ROOT)
    for base in targets(repo):
        base.mkdir(parents=True, exist_ok=True)
        for name in TEAM:
            dest = base / name
            if dest.exists():
                shutil.rmtree(dest)
            shutil.copytree(SKILLS / name, dest, ignore=shutil.ignore_patterns("__pycache__", ".DS_Store"))
            (dest / MARKER).write_text(json.dumps(
                {"source": "https://github.com/dca123/dev-skills", "path": f"skills/{name}", "commit": commit},
                indent=2) + "\n")
    claude = repo / ".claude/skills"
    if not claude.exists():
        claude.parent.mkdir(parents=True, exist_ok=True)
        claude.symlink_to(Path("../.agents/skills"))


def open_pr(repo: Path, base: str, dry_run: bool) -> None:
    if run("git", "status", "--porcelain", cwd=repo):
        sys.exit(f"{repo} has uncommitted changes; run sync from a clean worktree")
    short = run("git", "rev-parse", "--short", "HEAD", cwd=ROOT)
    branch = f"chore/sync-dev-skills-{short}"
    run("git", "fetch", "-q", "origin", base, cwd=repo)
    run("git", "checkout", "-q", "-B", branch, f"origin/{base}", cwd=repo)
    copy_skills(repo)
    # Force-add: a repo may ignore .claude/ (local settings) or .agents/; tracked files stay tracked.
    paths = [str(b.relative_to(repo) / n) for b in targets(repo) for n in TEAM] + [".claude/skills"]
    run("git", "add", "-f", *paths, cwd=repo)
    if not run("git", "status", "--porcelain", cwd=repo):
        print("already in sync; nothing to commit")
        return
    # Skill files are Markdown; repo formatters may be unavailable in a fresh worktree.
    env = {**os.environ, "LEFTHOOK_EXCLUDE": "preflight"}
    subprocess.run(["git", "commit", "-q", "-m", f"chore: sync team skills from dev-skills ({short})"],
                   cwd=repo, check=True, env=env)
    print(run("git", "show", "--stat", "--format=%h %s", "HEAD", cwd=repo))
    if dry_run:
        print(f"dry run: branch {branch} committed locally, not pushed")
        return
    run("git", "push", "-q", "-u", "origin", branch, cwd=repo)
    body = (ROOT / "scripts/pr-body.md").read_text()
    print(run("gh", "pr", "create", "--base", base, "--head", branch,
              "--title", "chore: add shared agent skills for tests, code smells and root-cause fixes",
              "--body", body, cwd=repo))


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check")
    c.add_argument("repo", type=Path)
    p = sub.add_parser("pr")
    p.add_argument("repo", type=Path)
    p.add_argument("--base", default="master")
    p.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    repo = args.repo.resolve()
    if args.cmd == "check":
        report = check(repo)
        print("\n".join(report) if report else "in sync")
        sys.exit(1 if report else 0)
    open_pr(repo, args.base, args.dry_run)


if __name__ == "__main__":
    main()
