# Reporting Issues & Feature Requests

We appreciate your help in making this project better! Whether you found a bug, ran into a layout problem, or want to suggest a new feature, your feedback is invaluable.

This guide outlines how to submit reports that can be triaged and resolved as quickly as possible.

---

## 🔍 Quick Checklist Before Submitting

To avoid duplicate work and resolve issues faster, please complete these steps before creating a new issue:

1. **Search Existing Issues**: Check the active and closed issues in the issue tracker to see if someone else has already reported the same problem.
2. **Update to Latest Version**: Verify that you are running the latest version of the project, as the issue may have already been resolved.
3. **Verify Configuration**: Make sure all environment variables, setups, and configuration settings are correct.

---

## 🐛 How to Report a Bug

To help us diagnose and fix the bug quickly, please include the following details in your report:

> [!IMPORTANT]
> The more detailed and reproducible your report is, the faster we can fix it.

### 1. Clear Summary
Provide a concise title that describes the issue clearly (e.g., *"validate_theme.py throws KeyError on optional translation files"* instead of *"It doesn't work"*).

### 2. Steps to Reproduce
List the exact steps someone else can follow to experience the issue:
1. Run `python3 validate_theme.py ...`
2. Pass argument `...`
3. See error `...`

### 3. Expected vs. Actual Behavior
- **Expected Behavior**: What you expected to happen.
- **Actual Behavior**: What actually happened (include error messages, console stack traces, or logs).

### 4. Screenshots or Screencasts
Visuals are extremely helpful for theme rendering, UI layout, or step-by-step flow issues. Drag and drop images or videos directly into the issue description.

### 5. System Environment
Include relevant details about the environment you are running:
- **Operating System**: (e.g., macOS Sonoma, Windows 11, Ubuntu 22.04)
- **Python Version**: (e.g., Python 3.10.12)
- **Node / ZCLI Version**: (if applicable)

---

## 💡 How to Request a Feature

If you have an idea for a new feature or improvement, feel free to open a feature request. Please structure your request as follows:

- **Problem Statement**: Describe the problem you are trying to solve or the limitation you face.
- **Proposed Solution**: Explain how you think the new feature should work.
- **Alternatives Considered**: Any alternative workarounds or designs you considered.
- **Context/Value**: Explain how this feature will benefit you and other users of the project.

---

## 🔒 Reporting Security Issues

> [!CAUTION]
> Do NOT report security vulnerabilities on the public issue tracker.

If you discover a security vulnerability, please report it responsibly per the instructions in [SECURITY.md](SECURITY.md).

---

## ⏱️ What Happens Next?

Once submitted:
1. **Triaging**: Maintainers will review the issue to classify it and verify reproducibility.
2. **Discussion**: We may ask clarifying questions or request additional logs.
3. **Resolution**: Once verified, a fix will be scheduled for development and released in a subsequent update.

Thank you for your cooperation and collaboration!
