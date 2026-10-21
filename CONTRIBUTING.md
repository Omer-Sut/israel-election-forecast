# Collaboration

## Repository and original bootstrap procedure

The public repository is https://github.com/Omer-Sut/israel-election-forecast. It has already been created. Use the clone and daily-work instructions below for normal collaboration. The following bootstrap instructions and publication helper are retained for reference; do not create the repository again.

If using the GitHub website instead, create an empty public repository under `Omer-Sut` with that name. Do not initialize a second README, license, or gitignore. Then, from this project directory:

```sh
git init -b main
git add README.md AGENTS.md CONTRIBUTING.md .gitignore .gitattributes docs scripts
git add -- '*.pdf'
git commit -m "Initialize election forecast project and competition context"
git remote add origin https://github.com/Omer-Sut/israel-election-forecast.git
git push -u origin main
```

If an `origin` already exists, inspect it before adding or changing remotes. Do not overwrite a repository with unrelated history.

## Another computer

After the first successful publication:

```sh
git clone https://github.com/Omer-Sut/israel-election-forecast.git
cd israel-election-forecast
git switch -c work/short-description
```

Clone separately on each computer. Use Git to exchange work; avoid using a concurrently synchronized OneDrive directory as the shared Git transport. A folder copy or cloud sync is not a replacement for committing and pushing.

Read the start-here documents before coding. There are currently no model dependencies to install.

## Daily work

1. Check `git status`, read the current handoff, and fetch remote changes.
2. Start a topic branch from an up-to-date `main`. Use `git pull --ff-only` on `main`; if it fails, inspect the divergence instead of forcing it.
3. Make a focused change and run relevant checks. Record data cutoffs and reproducibility details for experiments.
4. Update the state, session log, and decisions when applicable.
5. Inspect `git diff` and stage intended files explicitly. Commit and push the topic branch.
6. Open a pull request with the problem, resulting behavior, validation, and relevant limitations. Merge after review; resolve conflicts deliberately.

Git does not automatically synchronize edits. A change is available on another computer only after it is committed and pushed, then fetched/pulled there.

## Other people

A public repository permits reading and cloning. Direct write access requires the owner to invite collaborators through GitHub repository settings. Otherwise contributors can fork the repository and open pull requests. No collaborators have been invited yet, and no personal messages have been sent.

## Data and outputs

Small, redistributable, reproducibility-critical data snapshots can be tracked after reviewing licensing and contents. Raw/processed/local data directories are ignored by default. For data kept outside Git, document its location, access instructions, schema, version/hash, and retrieval procedure so another computer can reproduce the work. Do not commit private or restricted data simply to simplify setup.

There is no selected software license yet. Agree on one before representing the repository as open source.
