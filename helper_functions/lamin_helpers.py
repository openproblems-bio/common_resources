"""Shared steps of the scripts that store the data of a task in LaminDB.

Meant for the uv scripts in `scripts/` of a task repository, run from its root:

    sys.path.insert(0, "common/helper_functions")
    import lamin_helpers

The task is read from `_viash.yaml`, the instance from the `.lamin` directory in the root
of the repository.
"""

import subprocess
from pathlib import Path

import lamindb as ln
import yaml

INSTANCE = "openproblems/data-dev"


def git(*args):
  return subprocess.run(["git", *args], capture_output=True, text=True, check=True).stdout.strip()


REPO_ROOT = Path(git("rev-parse", "--show-toplevel"))
PROJECT_CONFIG = yaml.safe_load((REPO_ROOT / "_viash.yaml").read_text())
TASK = PROJECT_CONFIG["name"]
PROJECT = f"{PROJECT_CONFIG['organization']}/{TASK}"
REPO_URL = PROJECT_CONFIG["links"]["repository"]


def check_instance():
  """Make sure the .lamin dev-dir in the repo root selected the right instance."""
  instance = ln.setup.settings.instance.slug
  if instance != INSTANCE:
    raise RuntimeError(f"Connected to '{instance}' instead of '{INSTANCE}'")


def track(script):
  """Track a run of `script`, given as its path from the root of the repository.

  The run is labelled with the project of the task, which is created if needed.
  """
  check_instance()
  project = ln.Project.filter(name=PROJECT).one_or_none()
  if project is None:
    project = ln.Project(name=PROJECT, url=REPO_URL).save()
  # every task has its scripts at the same paths, so the task is part of the key
  ln.track(key=f"{TASK}/{script}", project=project)
  link_to_github(script)


def link_to_github(script):
  """Point the transform of the current run to the script on GitHub.

  Only done when the script is committed and pushed, so the link shows the code that ran.
  """
  commit = git("rev-parse", "HEAD")
  if git("status", "--porcelain", "--", str(REPO_ROOT / script)) or not git("branch", "-r", "--contains", commit):
    print(f"Not linking to GitHub: {script} has uncommitted or unpushed changes")
    return
  transform = ln.context.transform
  transform.reference = f"{REPO_URL}/blob/{commit}/{script}"
  transform.reference_type = "url"
  transform.save()


def save_collection(output_dir, files, key, description):
  """Store each file as an artifact under `key` and group them in a collection with that key.

  Earlier versions keep their files, so a pinned version of the collection stays downloadable.
  """
  artifacts = [
    ln.Artifact(
      Path(output_dir) / file,
      key=f"{key}/{file}",
      description=f"{description}: {file}",
      overwrite_versions=False,
    ).save()
    for file in files
  ]
  collection = ln.Collection(artifacts, key=key, description=description).save()
  print(f"lamin://{INSTANCE}/collection/{collection.uid}")
  return collection
