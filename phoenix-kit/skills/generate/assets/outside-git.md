# Outside a git repository: the baseline

`generate` checks with `git status` that no primitive changed. In a
folder that is not a git repository, use a hash baseline instead.

Step 1, before any code. Keep the file name that `mktemp` prints:

```sh
B=$(mktemp); find <primitive paths> -type f -not -path '*/__pycache__/*' \
  -not -name '*.pyc' | sort | xargs shasum -a 256 > "$B"; echo "$B"
```

Step 8, after the run. Run the same `find | shasum` line into a second
file, then `diff "$B" <second file>`. The output must be empty. Report it
as it is, file by file.

A test run writes cache files. The two `-not` filters leave them out, so
a cache file is not a change of a primitive.
