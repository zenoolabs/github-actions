Automated bump of `hubBackendVersion`: `{{PREVIOUS}}` → `{{VERSION}}`.

Triggered by a hub core release. This instance is subscribed via the `HUB_INSTANCE_SUBSCRIBERS` variable on the `hub` repo.

This PR is **not** auto-merged. The checks on it are the signal: if they fail, this hub core version broke something in this instance.

This is a rolling PR — a later hub core release force-updates this same branch rather than opening another PR, so there is at most one open bump PR here at a time.

<sub>Opened by the shared <a href="https://github.com/zenoolabs/github-actions/blob/main/.github/workflows/hub-core-bump.yml"><code>hub-core-bump</code></a> workflow. To unsubscribe, remove this repo from <code>HUB_INSTANCE_SUBSCRIBERS</code>.</sub>
