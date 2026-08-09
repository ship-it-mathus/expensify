# Git & Pull Request Workflow Rule

1. **Direct Pushes to Main Prohibited**: Never execute `git push origin main` directly, even if admin privileges allow bypassing rules.
2. **Feature Branching Required**: All edits, features, and UI modifications must be developed on a branch named `feat/<description>`.
3. **PR Link Generation**: After committing and pushing to `origin feat/<description>`, always provide a direct clickable link to create/merge the GitHub Pull Request.
