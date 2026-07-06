# Sandbox

Scratch space for trying out photos and captions before anything touches the real posting
schedule in `posts/`. Nothing in here gets published by the scheduler -- it only reads from
`posts/post-XX/`.

## Workflow

1. Create a folder for your test batch, e.g. `sandbox/test-batch/raw/`, and drop a few original
   (un-stamped) photos in there.
2. Once a logo file exists at `assets/shared/logos/logo.png`, run:
   ```bash
   python scripts/apply_logo_overlay.py --input sandbox/test-batch/raw --output sandbox/test-batch/final --corner bottom-right
   ```
   This writes logo-stamped copies into `sandbox/test-batch/final/` without touching the
   originals.
3. Review the stamped images and the draft captions (shared in chat / a `captions.md` file here)
   together.
4. Once approved, move the final images into the real `posts/post-XX/images/` folder (and the
   originals into `posts/post-XX/images/raw/` if you want to keep a backup), and drop the
   approved caption into that post's `post.json`.
