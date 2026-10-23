#!/usr/bin/env bash
# beforeShellExecution — defense-in-depth checks for recognizable commands.
# Reads the hook event JSON on stdin, prints {"permission": allow|ask|deny}.
#
# Regex checks are not a shell parser or a sandbox. Unknown programs, aliases,
# obfuscation and scripts can have effects these heuristics cannot establish.
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=guard.conf
[ -f "$HERE/guard.conf" ] && . "$HERE/guard.conf"
PY="$(command -v python3 || echo /usr/bin/python3)"

deny() {
  printf '{"permission":"deny","user_message":"Blocked by workspace hook: %s","agent_message":"Blocked by the workspace safety hook (.agent/hooks/guard-shell.sh): %s. Do not retry or work around it. Tell the user what you wanted to run and why."}\n' "$1" "$1"
  exit 0
}
ask() {
  printf '{"permission":"ask","user_message":"Needs approval: %s","agent_message":"This action needs the user'"'"'s explicit approval: %s. Wait for the decision."}\n' "$1" "$1"
  exit 0
}
case "${GUARD_PROFILE:-targeted}" in
  targeted|strict) ;;
  *) deny "invalid guard profile" ;;
esac
input="$(cat)"
if ! command="$(printf '%s' "$input" | "$PY" -c '
import json, sys
try:
    event = json.load(sys.stdin)
    command = event.get("command") if isinstance(event, dict) else None
    if not isinstance(command, str) or not command.strip() or "\0" in command:
        raise ValueError()
    print(command)
except (ValueError, TypeError):
    sys.exit(1)
')"; then
  deny "invalid hook event; command must be a nonempty string"
fi
match_command() {
  local status=0
  printf '%s' "$command" | grep "$1" -e "$2" || status=$?
  [ "$status" -le 1 ] || deny "invalid shell guard pattern"
  return "$status"
}
m() { match_command -qE "$1"; }
mi() { match_command -qiE "$1"; }

# ---------------------------------------------------------------- destructive
m 'rm\s+(-[a-zA-Z]*r[a-zA-Z]*f|-[a-zA-Z]*f[a-zA-Z]*r)[a-zA-Z]*\s+("?(/|~|\$HOME)"?(\s|$)|~/(Documents|Desktop|Library|Downloads|Pictures)/?(\s|$))' \
  && deny "recursive force-delete of a home or system path"
# `git -C <dir> ...` is the same command aimed at a nested repo; match it too.
m 'git(\s+-C\s+\S+)?\s+push\b[^|;&]*(--force\b|--force-with-lease\b|[[:space:]]-f\b)' \
  && deny "git force-push"
m 'git(\s+-C\s+\S+)?\s+(reset\s+--hard|clean\s+-[a-zA-Z]*[fd]|checkout\s+\.|restore\s+\.|filter-branch|rebase\s+.*--root)' \
  && deny "discards uncommitted work or rewrites history"
m 'git(\s+-C\s+\S+)?\s+(branch\s+-D|push\b[^|;&]*--delete|tag\s+-d)' \
  && ask "deletes a branch or tag"
m '(mkfs|diskutil\s+(erase|reformat)|dd\s+.*of=/dev/)' \
  && deny "disk-level destructive operation"

# ---------------------------------------------------------------- isolation
if [ -n "${PROTECTED_PATHS:-}" ]; then
  m "$PROTECTED_PATHS" && deny "touches a protected path outside this workspace"
fi

# ---------------------------------------------------------------- credentials
SECRET_FILES='(\.env(\.[a-z]+)?\b|id_rsa|id_ed25519|\.pem\b|\.p12\b|\.keystore\b|credentials|\.netrc|\.npmrc|\.pypirc|\.codex/auth\.json|\.aws/|\.ssh/|Keychains?|mcp\.json|accounts_pool)'
# Inspect reader operands, not search expressions or other command text. Shell
# syntax is tokenized only; no command, expansion or substitution is executed.
credential_action="$(printf '%s' "$command" | "$PY" -c '
import fnmatch, os, re, shlex, sys

extra = sys.argv[1].split()
hard = (
    r"(^|/)(id_rsa|id_ed25519)[^/]*($|/)", r"\.(pem|p12|keystore|jks|pfx)$",
    r"(^|/)(\.ssh|\.aws)(/|$)", r"(^|/)(\.netrc|\.npmrc|\.pypirc)$",
    r"(^|/)mcp\.json$", r"(^|/)\.codex/auth\.json$",
    r"(^|/)\.claude/settings\.local\.json$", r"(^|/)Keychains?(/|$)", r"accounts_pool",
)

def secret(path):
    remote = path.split(":", 1)[1] if re.match(r"^[^/]+:", path) else path
    for candidate in {path, remote, os.path.abspath(path), os.path.realpath(path)}:
        if any(re.search(pattern, candidate) for pattern in hard):
            return True
        if any(fnmatch.fnmatchcase(candidate, pattern) for pattern in extra):
            return True
        location = candidate if os.path.isabs(candidate) else os.path.join(os.getcwd(), candidate)
        source = re.search(r"(^|/)(src|app|lib|tests?|tools|scripts|automation|packages)/", location)
        source = source and re.search(r"\.(py|[cm]?js|jsx|ts|tsx|sh|bash|zsh|rb|rs|go|java|kt|kts|swift|cs|c|cpp|h|hpp|php)$", location)
        source = source and not re.search(r"credentials($|[./])", os.path.dirname(location))
        if re.search(r"credentials($|[./])", candidate) and not source:
            return True
        if not candidate.endswith((".example", ".template", ".sample")) and re.search(r"\.env($|[./])", candidate):
            return True
    return False

readers = {"cat", "less", "more", "head", "tail", "bat", "xxd", "strings", "base64", "scp", "rsync", "sqlite3", "source", "."}
searches = {"rg", "grep", "sed", "awk", "jq", "yq"}

def options(flags="", long_flags="", **groups):
    spec = {"-" + flag: "flag" for flag in flags}
    spec.update({"--" + flag: "flag" for flag in long_flags.split()})
    for kind, names in groups.items():
        spec.update({name: kind for name in names.split()})
    return spec

specs = {
    "rg": options("nivwxlsqSUHhaFPLuozcIN01V", "files hidden no-hidden no-ignore no-ignore-vcs no-ignore-parent no-ignore-global no-ignore-dot no-config follow fixed-strings ignore-case case-sensitive smart-case line-number no-line-number with-filename no-filename only-matching invert-match word-regexp line-regexp count count-matches files-with-matches files-without-match json stats no-stats debug trace no-messages messages multiline multiline-dotall text binary null null-data heading no-heading passthru pcre2 crlf trim search-zip",
        pattern="-e --regexp", programfile="-f --file", file="--ignore-file",
        glob="-g --glob --iglob", value="-m --max-count -j --threads -A --after-context -B --before-context -C --context -t --type -T --type-not -r --replace -M --max-columns --max-depth --max-filesize --encoding --color --colors --sort --sortr --type-add --type-clear --field-match-separator --field-context-separator"),
    "grep": options("EFGPnivwxlsqHhaILRroUubczZ", "extended-regexp fixed-strings basic-regexp perl-regexp ignore-case invert-match word-regexp line-regexp line-number with-filename no-filename files-with-matches files-without-match count quiet silent no-messages recursive dereference-recursive text only-matching null null-data",
        pattern="-e --regexp", programfile="-f --file", file="--exclude-from", glob="--include",
        value="-m --max-count -A --after-context -B --before-context -C --context --label --exclude --exclude-dir --binary-files", optional="--color --colour"),
    "sed": options("nErsuz", "quiet silent regexp-extended separate unbuffered null-data",
        pattern="-e --expression", programfile="-f --file"),
    "awk": options("", "posix traditional", programfile="-f --file", value="-v --assign -F --field-separator"),
    "jq": options("necsrRMCSja", "null-input exit-status compact-output slurp raw-input raw-output monochrome-output color-output sort-keys join-output ascii-output unbuffered seq stream",
        programfile="-f --from-file", arg="--arg --argjson", filearg="--slurpfile --rawfile", file="-L", value="--indent"),
    "cat": options("AbeEnstTuv", "show-all number-nonblank show-ends number squeeze-blank show-tabs show-nonprinting"),
    "less": options("NSRFXqQeEfsiIwWMmngG", "", value="-p -P -x -j -z"),
    "more": options("dlfpcsuv", "", value="-n"),
    "head": options("qv", "quiet silent verbose", value="-n --lines -c --bytes"),
    "tail": options("fFqv", "quiet silent verbose retry", value="-n --lines -c --bytes --pid --sleep-interval"),
    "bat": options("npAP", "plain number show-all", value="-l --language --style --theme --paging --color --terminal-width --line-range", opaque="--pager"),
    "xxd": options("Eabhipruv", "", value="-c -g -l -o -s"),
    "strings": options("afoTv", "all print-file-name", value="-n --bytes -t --radix -e --encoding -s --output-separator"),
    "base64": options("dD", "decode ignore-garbage", file="-i --input -o --output", value="-b -w --wrap"),
    "scp": options("rpqvCB346OTA", "", file="-i -F -S -o", value="-J -P -c -l"),
    "rsync": options("avrzPqclptgoDHxSRWunIOLK", "archive verbose recursive compress progress quiet checksum links perms times group owner devices specials hard-links one-file-system sparse relative whole-file update dry-run ignore-times omit-dir-times copy-links keep-dirlinks delete delete-after delete-before delete-delay existing ignore-existing size-only itemize-changes stats human-readable partial inplace",
        file="--files-from --exclude-from --include-from --password-file", value="--exclude --filter --bwlimit --timeout --contimeout --max-size --min-size --out-format --chmod --chown --backup-dir --suffix --temp-dir --partial-dir", glob="--include", opaque="--rsync-path -e"),
    "sqlite3": options("", "batch column csv echo header html line list readonly table tabs version", file="-init --init", opaque="-cmd --cmd", value="-separator --separator -nullvalue --nullvalue"),
    "source": options(), ".": options(),
    "cp": options("aRrPpfinvHLT", "archive recursive no-dereference preserve force interactive no-clobber verbose parents remove-destination", file="-t --target-directory"),
    "mv": options("finvT", "force interactive no-clobber verbose", file="-t --target-directory"),
}
specs["yq"] = specs["jq"]
for spec in specs.values():
    spec.update({"--help": "flag", "--version": "flag"})

# A supported flag has explicit arity. Unsupported reader options retain all
# possible file operands and require review instead of guessing their meaning.
def parse_options(args, spec, stop_at_positional=False):
    items, positional, ambiguous, index, literal = [], [], False, 0, False
    while index < len(args):
        arg = args[index]
        index += 1
        if literal or not arg.startswith("-") or arg == "-":
            positional.append(arg)
            if stop_at_positional:
                positional.extend(args[index:])
                break
            continue
        if arg == "--":
            literal = True
            continue
        pending = []
        if arg in spec or arg.startswith("--"):
            option, equal, value = arg.partition("=")
            pending = [(option, value if equal else None)]
        else:
            for offset, flag in enumerate(arg[1:], 1):
                option = "-" + flag
                if spec.get(option) not in ("flag", "netrc"):
                    pending.append((option, arg[offset + 1:] or None))
                    break
                pending.append((option, None))
        for option, attached in pending:
            kind = spec.get(option)
            if kind is None or kind in ("flag", "netrc") and attached is not None:
                ambiguous = True
                continue
            if kind in ("flag", "netrc"):
                items.append((option, kind, []))
                continue
            if kind == "optional":
                items.append((option, kind, [attached] if attached is not None else []))
                continue
            count = 2 if kind in ("arg", "filearg") else 1
            values = [attached] if attached is not None else []
            needed = count - len(values)
            values.extend(args[index:index + needed])
            index += needed
            if len(values) != count:
                ambiguous = True
            if kind == "opaque":
                ambiguous = True
            items.append((option, kind, values))
    return items, positional, ambiguous

def operands(name, args):
    items, positional, ambiguous = parse_options(args, specs[name])
    paths, programs = [], []
    program = name in searches and "--files" not in args
    for option, kind, values in items:
        if kind in ("file", "programfile", "filearg"):
            paths.extend(values[-1:])
        if kind == "glob":
            paths.extend(value for value in values if not value.startswith("!"))
        if kind == "pattern":
            programs.extend(values)
        if kind in ("pattern", "programfile"):
            program = False
    if program and positional:
        programs.append(positional.pop(0))
    if name in ("sed", "awk", "jq", "yq"):
        for expression in programs:
            for literal in re.findall(r"\"([^\"]*)\"", expression):
                paths.extend(re.split(r"[\s;|&]+", literal))
            if name == "sed":
                paths.extend(re.findall(r"(?:^|[;}])\s*(?:[0-9]+|/[^/]*/)?\s*[rRe]\s+(.+)", expression))
    if ambiguous:
        paths.extend(args)
    return paths + positional, ambiguous

network_specs = {
    "curl": options("aBfGgIikjLlMnNOpqRsSvVZ046123J#", "anyauth basic compressed compressed-ssh create-dirs crlf digest disable-eprt disable-epsv fail-early fail-with-body globoff http0.9 http1.1 http2 http2-prior-knowledge http3 http3-only ignore-content-length include insecure ipv4 ipv6 junk-session-cookies location location-trusted manual negotiate no-alpn no-buffer no-clobber no-keepalive no-npn no-progress-meter no-sessionid ntlm ntlm-wb parallel parallel-immediate path-as-is post301 post302 post303 progress-bar proxytunnel raw remote-header-name remote-name remote-name-all remote-time remove-on-error retry-all-errors retry-connrefused show-error silent ssl ssl-reqd styled-output suppress-connect-headers tcp-fastopen tcp-nodelay tlsv1 tlsv1.0 tlsv1.1 tlsv1.2 tlsv1.3 tr-encoding verbose version xattr",
        file="-T --upload-file -K --config --netrc-file --key --cacert --capath --crlfile --egd-file --etag-compare --hsts --alt-svc --pubkey --random-file --proxy-key --proxy-cacert --proxy-capath --proxy-crlfile -o --output --output-dir -D --dump-header -c --cookie-jar --etag-save --libcurl --stderr --trace --trace-ascii",
        certificate="-E --cert --proxy-cert", cookie="-b --cookie", header="-H --header --proxy-header -w --write-out",
        data="-d --data --data-ascii --data-binary --json", urlencode="--data-urlencode --url-query", form="-F --form", url="--url",
        value="--data-raw --form-string -X --request -A --user-agent -u --user -U --proxy-user -x --proxy --preproxy --noproxy -m --max-time --connect-timeout --retry --retry-delay --retry-max-time --max-redirs --max-filesize --limit-rate --rate --parallel-max --connect-to --resolve --interface --unix-socket --abstract-unix-socket --socks4 --socks4a --socks5 --socks5-hostname --local-port --proto --proto-default --proto-redir -Q --quote -r --range -e --referer"),
    "wget": options("qvcbNnHpkKEmr", "quiet verbose no-verbose continue background timestamping no-host-directories page-requisites convert-links backup-converted adjust-extension mirror recursive spider no-check-certificate",
        file="-i --input-file --config --post-file --body-file --load-cookies --certificate --private-key --ca-certificate --random-file --egd-file -O --output-document -o --output-file -a --append-output", value="-t --tries -T --timeout -U --user-agent --method --post-data --body-data --header --user --password --http-user --http-password --proxy-user --proxy-password --limit-rate --wait --waitretry --directory-prefix -P --level -l --accept -A --reject -R --domains -D --exclude-domains"),
}

def network_operands(name, args):
    from urllib.parse import unquote, urlsplit
    spec = dict(network_specs[name])
    if name == "curl":
        spec.update({"-n": "netrc", "--netrc": "netrc", "--netrc-optional": "netrc"})
    items, positional, ambiguous = parse_options(args, spec)
    paths, urls = [], list(positional)
    for option, kind, values in items:
        if kind == "netrc":
            paths.append(".netrc")
        for value in values:
            if kind == "file":
                paths.append(value)
            elif kind == "certificate":
                paths.append(value.split(":", 1)[0])
            elif kind == "cookie" and "=" not in value:
                paths.append(value)
            elif kind in ("data", "header", "urlencode"):
                if value.startswith("@"):
                    paths.append(value[1:])
                elif kind == "urlencode" and "@" in value and "=" not in value.split("@", 1)[0]:
                    paths.append(value.split("@", 1)[1])
            elif kind == "form" and "=" in value:
                content = value.split("=", 1)[1]
                if content.startswith(("@", "<")):
                    paths.extend(content[1:].split(";", 1)[0].split(","))
            elif kind == "url":
                urls.append(value)
    for url in urls:
        if url.lower().startswith("file:"):
            paths.append(unquote(urlsplit(url).path))
    if ambiguous:
        paths.extend(args)
    return paths, ambiguous

wrapper_specs = {
    "env": options("iv0", "ignore-environment null debug", value="-u --unset -P --path", context="-C --chdir --argv0", split="-S --split-string"),
    "sudo": options("AbEHknPSVv", "askpass background set-home preserve-env non-interactive stdin remove-timestamp reset-timestamp version validate",
        value="-u --user -g --group -C --close-from -p --prompt -r --role -t --type -T --command-timeout", context="-D --chdir -R --chroot"),
    "command": options("pvV"), "builtin": options(), "exec": options("cl", "", value="-a"),
    "time": options("p"), "nohup": options(),
    "xargs": options("0prt", "null no-run-if-empty interactive verbose",
        value="-I --replace -n --max-args -P --max-procs -L --max-lines -d --delimiter -E --eof -s --max-chars"),
}

def unwrap(words):
    ambiguous, uncertain, hops = False, False, 0
    while words:
        hops += 1
        if hops > 32:
            return words, True, True
        if re.match(r"^[A-Za-z_][A-Za-z_0-9]*=", words[0]) or words[0] in ("then", "do", "else", "{", "!"):
            words = words[1:]
            continue
        wrapper = os.path.basename(words[0])
        if wrapper not in wrapper_specs:
            break
        items, rest, unknown = parse_options(words[1:], wrapper_specs[wrapper], stop_at_positional=True)
        uncertain = uncertain or unknown
        for option, kind, values in items:
            if kind == "context":
                ambiguous = True
            if kind == "split" and values:
                value = values[0]
                if any(char in value for char in ("\\", "$", chr(96), "\n", "\r")):
                    uncertain = True
                else:
                    try:
                        rest = ["env"] + shlex.split(value) + rest
                    except ValueError:
                        uncertain = True
        words = rest
    return words, ambiguous or uncertain, uncertain

def inspect(command, depth=0):
    if depth > 3:
        return "deny"
    action = "allow"
    for nested in re.findall(r"`([^`]*)`", command):
        nested_action = inspect(nested, depth + 1)
        if nested_action == "deny":
            return "deny"
        if nested_action == "ask":
            action = "ask"
    try:
        lexer = shlex.shlex(command, posix=True, punctuation_chars=";&|()<>\n")
        lexer.whitespace = " \t\r"
        lexer.whitespace_split = True
        lexer.commenters = ""
        words = list(lexer)
    except ValueError:
        return "deny"
    segments, current = [], []
    for word in words + [";"]:
        if word and all(char in ";&|()\n" for char in word):
            if current:
                segments.append(current)
            current = []
        else:
            current.append(word)
    for segment in segments:
        clean, index = [], 0
        while index < len(segment):
            word = segment[index]
            if word and all(char in "<>" for char in word):
                if index + 1 < len(segment) and word in ("<", "<>") and secret(segment[index + 1]):
                    return "deny"
                index += 2
            else:
                clean.append(word)
                index += 1
        clean, wrapper_ask, unknown_wrapper = unwrap(clean)
        if unknown_wrapper and any(secret(word) for word in segment):
            return "deny"
        if wrapper_ask:
            action = "ask"
        if not clean:
            continue
        name, args = os.path.basename(clean[0]), clean[1:]
        if name in readers | searches:
            paths, ambiguous = operands(name, args)
            if any(secret(path) for path in paths):
                return "deny"
            if ambiguous:
                action = "ask"
        elif name in ("curl", "wget"):
            paths, ambiguous = network_operands(name, args)
            if any(secret(path) for path in paths):
                return "deny"
            if ambiguous:
                action = "ask"
        elif name in ("cp", "mv"):
            paths, ambiguous = operands(name, args)
            template = len(paths) == 2 and paths[0].endswith((".example", ".template", ".sample")) and not secret(paths[0])
            if ambiguous or any(secret(path) for path in paths) and not template:
                action = "ask"
        elif name in ("sh", "bash", "zsh") and any(re.fullmatch(r"-[a-z]*c[a-z]*", arg) for arg in args):
            index = next(index for index, arg in enumerate(args) if re.fullmatch(r"-[a-z]*c[a-z]*", arg)) + 1
            if index < len(args):
                nested = inspect(args[index], depth + 1)
                if nested == "deny":
                    return nested
                if nested == "ask":
                    action = nested
    return action

print(inspect(sys.stdin.read()))
' "${EXTRA_DENY_READ:-}")"
case "$credential_action" in
  deny) deny "reads or copies credential material" ;;
esac
# Keep conservative interpreter checks: their program strings are not ordinary
# reader operands and may encode file access in arbitrary language syntax.
scrubbed="$(printf '%s' "$command" | sed -E 's#[^[:space:]"'"'"'=;|&()]*\.(example|template|sample)([[:space:]"'"'"'=;|&()]|$)#\2#g')"
ms() { printf '%s' "$scrubbed" | grep -qE -e "$1"; }
# interpreters take a quoted program that may itself contain ; & | — scan to end of line
ms "(python3?|node|ruby|perl|php|deno|bun)\\b.*${SECRET_FILES}" \
  && deny "interpreter reads credential material"
ms "(^|[;&|]\\s*)\\.\\s+[^|;&]*${SECRET_FILES}" \
  && deny "sources a credential file into the shell"
m '(\.env|secret|token|password|credential|PMAK|PAT)[^|;&]*\|[^|;&]*(curl|wget|nc)\b' \
  && deny "possible credential exfiltration"
m 'security\s+find-(generic|internet)-password' \
  && deny "dumps a keychain secret into the agent context"

# ---------------------------------------------------------------- production
# A test runner or mutation script pointed at production is denied outright.
# Release and production checks are human actions.
if [ -n "${TEST_RUNNERS:-}" ] && [ -n "${PROD_SELECTORS:-}" ]; then
  if m "$TEST_RUNNERS" && mi "$PROD_SELECTORS"; then
    deny "test or mutation run targets production"
  fi
fi
mi '(TEST_ENVIRONMENT|[A-Z_]*_ENV|ENVIRONMENT)=("?)(prod|production)\b' \
  && deny "environment variable selects production"

# ---------------------------------------------------------------- ask
if [ -n "${EXTRA_DENY:-}" ]; then m "$EXTRA_DENY" && deny "workspace-specific denied action"; fi
[ "$credential_action" != ask ] || ask "credential-file copy or unclassified reader arguments"
if [ -n "${EXTRA_ASK:-}" ];  then m "$EXTRA_ASK"  && ask  "workspace-specific gated action";  fi

m '(vercel\s+.*--prod|eas\s+(submit|build\s+.*--auto-submit)|npm\s+publish|supabase\s+db\s+push|gh\s+release\s+create|gh\s+pr\s+merge)' \
  && ask "deployment, release or merge action"
mi '(drop\s+(table|database|schema)|truncate\s+table|delete\s+from\s+[a-z_]+\s*(;|$)|update\s+[a-z_]+\s+set\b[^;]*$)' \
  && ask "destructive or unbounded database mutation"

if [ "${GUARD_PROFILE:-targeted}" = strict ]; then
m '((npm|pnpm|bun)\s+(i|install|add)|yarn\s+add|pip3?\s+install|uv\s+(add|pip\s+install)|brew\s+install|cargo\s+add|dotnet\s+add\s+package|gem\s+install|go\s+get)\s+[^-[:space:]]' \
  && ask "adds a new dependency under the strict profile"
m '--confirm-write|push-collection' && ask "strict profile gates workspace writes"
# These common CLI spellings are gated even when no MCP connector is involved.
# They intentionally do not claim to classify arbitrary programs or API effects.
m '(acli|twg)\b[^|;&]*\b(create|update|edit|delete|remove|transition|assign|post|send|publish|write|upload|add|set|close|reopen)\b' \
  && ask "tracker or workspace CLI mutation"
m 'gh\s+(issue|pr|release|repo|project|label|gist)\b[^|;&]*\b(create|edit|comment|close|reopen|merge|review|ready|lock|unlock|delete|archive|transfer|add|remove)\b' \
  && ask "GitHub CLI mutation"
mi '(gh\s+api|az\s+rest)\b[^|;&]*(-X[[:space:]]*|--method[=[:space:]]+)(POST|PUT|PATCH|DELETE)\b' \
  && ask "API mutation method"
m 'gh\s+api\b[^|;&]*([[:space:]]-[fF]([[:space:]]|[^-[:space:]])|--(raw-)?field([=[:space:]]))' \
  && ask "GitHub API fields can imply a POST request"
m 'az\b[^|;&]*\b(create|update|delete|set|start|stop|restart|deallocate|redeploy|assign|remove|add|upload|import|restore|swap)\b' \
  && ask "cloud CLI mutation"
mi '(curl\b[^|;&]*(-X[[:space:]]*|--request[=[:space:]]+)(POST|PUT|PATCH|DELETE)\b|curl\b[^|;&]*([[:space:]]-[dFT]([[:space:]]|[^-[:space:]])|--(data[^[:space:]]*|form|upload-file)([=[:space:]]))|wget\b[^|;&]*--(post-data|post-file|method[=[:space:]]+(POST|PUT|PATCH|DELETE)))' \
  && ask "HTTP request may mutate external state"
fi

printf '{"permission":"allow"}\n'
