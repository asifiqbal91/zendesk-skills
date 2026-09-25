#!/usr/bin/env python3
"""
deploy_theme.py — package, import/update, and (optionally) publish a Zendesk
Guide Help Center theme via the Themes API. Suitable for CI.

Auth (env vars):
    ZD_SUBDOMAIN   your-subdomain (the account subdomain; use the account
                   domain, not a brand domain, when multi-brand)
    ZD_EMAIL       agent email
    ZD_API_TOKEN   API token  (basic auth uses "{email}/token:{api_token}")

Usage:
    # import a new theme into a brand, then publish
    python3 deploy_theme.py ./my-theme --brand-id 360001234567 --publish

    # update an existing theme in place (keeps current settings unless --replace-settings)
    python3 deploy_theme.py ./my-theme --theme-id 01H... --publish

Requires: pip install requests
Recommended: run validate_theme.py first so a bad theme never reaches upload.

Note on the upload step: the storage endpoint is an S3-style presigned POST, so
the "file" field must be sent AFTER all returned parameters. requests orders
`data` fields before `files`, which satisfies this; if you reimplement the POST
by hand, preserve that ordering.

Flow (per Themes API):
    import: create import job -> upload zip to one-time storage URL (no auth) ->
            poll job -> theme_id ready
    update: create update job -> upload zip -> poll job
    publish: POST /themes/{id}/publish
"""

import argparse
import io
import os
import sys
import time
import zipfile
from pathlib import Path

import requests

API = "https://{sub}.zendesk.com/api/v2/guide/theming"
POLL_SECONDS = 5
POLL_MAX_ATTEMPTS = 60  # ~5 min


def auth():
    sub = os.environ.get("ZD_SUBDOMAIN")
    email = os.environ.get("ZD_EMAIL")
    token = os.environ.get("ZD_API_TOKEN")
    if not all([sub, email, token]):
        sys.exit("Set ZD_SUBDOMAIN, ZD_EMAIL, ZD_API_TOKEN.")
    return sub, (f"{email}/token", token)


def zip_theme(theme_dir: Path) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for f in theme_dir.rglob("*"):
            if f.is_file() and "node_modules" not in f.parts and not f.name.startswith("."):
                z.write(f, f.relative_to(theme_dir).as_posix())
    return buf.getvalue()


def create_job(sub, creds, kind, attributes):
    url = f"{API.format(sub=sub)}/jobs/themes/{kind}"
    r = requests.post(url, json={"job": {"attributes": attributes}}, auth=creds)
    r.raise_for_status()
    return r.json()["job"]


def upload_zip(upload, zip_bytes):
    # POST the zip to the one-time storage URL with NO auth headers.
    # All returned parameters become form fields; the file field is last.
    fields = dict(upload["parameters"])
    files = {"file": ("theme.zip", zip_bytes, "application/zip")}
    r = requests.post(upload["url"], data=fields, files=files)
    r.raise_for_status()


def poll(sub, creds, job_id):
    url = f"{API.format(sub=sub)}/jobs/{job_id}"
    for _ in range(POLL_MAX_ATTEMPTS):
        r = requests.get(url, auth=creds)
        r.raise_for_status()
        job = r.json()["job"]
        if job["status"] != "pending":
            return job
        time.sleep(POLL_SECONDS)
    sys.exit("Timed out polling job.")


def publish(sub, creds, theme_id):
    url = f"{API.format(sub=sub)}/themes/{theme_id}/publish"
    r = requests.post(url, auth=creds)
    r.raise_for_status()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("theme_dir", type=Path)
    ap.add_argument("--brand-id")
    ap.add_argument("--theme-id")
    ap.add_argument("--replace-settings", action="store_true")
    ap.add_argument("--publish", action="store_true")
    args = ap.parse_args()

    sub, creds = auth()
    zip_bytes = zip_theme(args.theme_dir)

    if args.theme_id:
        job = create_job(sub, creds, "updates", {
            "theme_id": args.theme_id, "replace_settings": args.replace_settings, "format": "zip"})
        theme_id = args.theme_id
    elif args.brand_id:
        job = create_job(sub, creds, "imports", {"brand_id": args.brand_id, "format": "zip"})
        theme_id = job["data"]["theme_id"]
    else:
        sys.exit("Provide --brand-id (import) or --theme-id (update).")

    upload_zip(job["data"]["upload"], zip_bytes)
    done = poll(sub, creds, job["id"])
    if done["status"] == "failed":
        sys.exit(f"Job failed: {done.get('errors')}")
    print(f"Theme ready: {theme_id}")

    if args.publish:
        publish(sub, creds, theme_id)
        print("Published.")


if __name__ == "__main__":
    main()
