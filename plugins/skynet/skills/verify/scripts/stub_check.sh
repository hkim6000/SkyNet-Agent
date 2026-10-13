#!/usr/bin/env bash
set -euo pipefail
SITE="$(cd "${1:?usage: stub_check.sh <site-folder> [namespace]}" && pwd)"
NS="${2:-$(basename "$SITE")}"
HERE="$(cd "$(dirname "$0")/.." && pwd)"
WORK="${SKYNET_CHECK_DIR:-${TMPDIR:-/tmp}/skynet-check-$NS}"
mkdir -p "$WORK"
cp "$HERE/harness/Stub.cs" "$HERE/harness/SqlStub.cs" "$HERE/harness/Runner.cs" "$HERE/harness/check.csproj" "$HERE/harness/nuget.config" "$WORK/"
MAJOR="$(dotnet --version | cut -d. -f1)"
dotnet build "$WORK/check.csproj" -nologo -v q -p:SiteRoot="$SITE" -p:TargetFramework="net$MAJOR.0" -o "$WORK/out" 2>&1 | grep -E "error|warning|Warn|Error" | sort -u
echo "runner: SKYNET_ROOT=\"$SITE\" SKYNET_NS=\"$NS\" \"$WORK/out/skynetcheck\" get Home"
