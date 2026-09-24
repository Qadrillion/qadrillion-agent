#!/usr/bin/env python3
"""Build and own a disposable native Android reference target, without Gradle."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import time
import uuid
import zipfile

SOURCE = Path(__file__).resolve().parent
PACKAGE = "com.qadrillion.parcel"
MARKER = "qadrillion-mobile-demo-v1"


def execute(args, env=None, timeout=120, input_text=None):
    return subprocess.run([str(arg) for arg in args], env=env, input=input_text,
                          text=True, capture_output=True, timeout=timeout)


def checked(args, env, log, input_text=None):
    result = execute(args, env, input_text=input_text)
    with log.open("a") as stream:
        stream.write(json.dumps([str(arg) for arg in args]) + "\n")
        stream.write(result.stdout + result.stderr + f"\nexit={result.returncode}\n")
    if result.returncode:
        raise RuntimeError(f"{Path(args[0]).name} exited {result.returncode}; see {log}")
    return result.stdout


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def environment(state, root):
    env = dict(os.environ)
    env.update(JAVA_HOME=state["java_home"], ANDROID_HOME=state["sdk"],
               ANDROID_USER_HOME=str(root / "android-user"),
               ANDROID_AVD_HOME=str(root / "avd"))
    env.pop("ANDROID_SDK_ROOT", None)
    return env


def save(root, state):
    (root / "run.json").write_text(json.dumps(state, indent=2) + "\n")


def load(root):
    state = json.loads((root / "run.json").read_text())
    if state.get("owner") != MARKER or state.get("root") != str(root):
        raise RuntimeError("Run identity does not match this directory")
    expected = "qa-mobile-" + state["id"]
    if state.get("avd_name") != expected:
        raise RuntimeError("AVD ownership marker is invalid")
    return state


def tool(state, relative):
    return Path(state["sdk"]) / relative


def adb(state, *args):
    return execute([tool(state, "platform-tools/adb"), "-s", state["serial"], *args],
                   timeout=20)


def assert_device(state):
    result = adb(state, "emu", "avd", "name")
    if result.returncode or result.stdout.splitlines()[:1] != [state["avd_name"]]:
        raise RuntimeError("Device is absent or its AVD identity does not match this run")


def prepare(args, root):
    sdk = Path(args.sdk).expanduser().resolve()
    java_home = Path(args.java_home).expanduser().resolve()
    required = [sdk / "platform-tools/adb", sdk / "emulator/emulator",
                sdk / "cmdline-tools/latest/bin/avdmanager",
                sdk / f"platforms/android-{args.api}/android.jar",
                sdk / "system-images" / Path(*args.image.split(";")[1:]) / "system.img",
                java_home / "bin/javac", java_home / "bin/keytool"]
    required += [sdk / "build-tools" / args.build_tools / name
                 for name in ("aapt2", "d8", "zipalign", "apksigner")]
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        raise RuntimeError("Missing dependencies: " + ", ".join(missing))
    root.mkdir(parents=True, exist_ok=False)
    run_id = uuid.uuid4().hex[:12]
    state = dict(owner=MARKER, root=str(root), id=run_id,
                 avd_name="qa-mobile-" + run_id, sdk=str(sdk), java_home=str(java_home),
                 api=args.api, build_tools=args.build_tools, image=args.image, builds={})
    save(root, state)
    env = environment(state, root)
    for name in ("avd", "android-user", "evidence"):
        (root / name).mkdir()
    key = root / "fixture-only.p12"
    checked([java_home / "bin/keytool", "-genkeypair", "-keystore", key,
             "-storepass", "android", "-keypass", "android", "-alias", "fixture",
             "-keyalg", "RSA", "-keysize", "2048", "-validity", "7",
             "-dname", "CN=Disposable QA fixture"], env, root / "build.log")
    for variant in ("baseline", "seeded"):
        build(root, state, env, variant, key)
    save(root, state)
    print(json.dumps(state, indent=2))


def build(root, state, env, variant, key):
    output = root / variant
    output.mkdir()
    for name in ("generated", "classes", "dex"):
        (output / name).mkdir()
    log = root / "build.log"
    bt = tool(state, "build-tools") / state["build_tools"]
    android = tool(state, f"platforms/android-{state['api']}/android.jar")
    checked([bt / "aapt2", "compile", "--dir", SOURCE / "res",
             "-o", output / "resources.zip"], env, log)
    checked([bt / "aapt2", "link", "-o", output / "unsigned.apk",
             "-I", android, "--manifest", SOURCE / "AndroidManifest.xml",
             "--java", output / "generated", output / "resources.zip"], env, log)
    config = output / "generated/com/qadrillion/parcel/BuildConfig.java"
    config.write_text("package com.qadrillion.parcel;\npublic final class BuildConfig {\n"
                      " public static final boolean SAVE_TOTAL = " +
                      ("true" if variant == "baseline" else "false") + ";\n}\n")
    checked([Path(state["java_home"]) / "bin/javac", "-source", "8", "-target", "8",
             "-classpath", android, "-d", output / "classes", SOURCE / "MainActivity.java",
             *sorted((output / "generated").rglob("*.java"))], env, log)
    checked([bt / "d8", "--lib", android, "--min-api", "26",
             "--output", output / "dex", *sorted((output / "classes").rglob("*.class"))], env, log)
    with zipfile.ZipFile(output / "unsigned.apk", "a") as archive:
        archive.write(output / "dex/classes.dex", "classes.dex")
    checked([bt / "zipalign", "-f", "4", output / "unsigned.apk",
             output / "aligned.apk"], env, log)
    apk = output / "parcel.apk"
    checked([bt / "apksigner", "sign", "--ks", key, "--ks-key-alias", "fixture",
             "--ks-pass", "pass:android", "--out", apk, output / "aligned.apk"], env, log)
    checked([bt / "apksigner", "verify", "--verbose", apk], env, log)
    state["builds"][variant] = {"apk": str(apk), "sha256": digest(apk)}
    state["source_sha256"] = {str(path.relative_to(SOURCE)): digest(path)
                              for path in (SOURCE / "MainActivity.java",
                                           SOURCE / "AndroidManifest.xml",
                                           SOURCE / "res/values/ids.xml")}


def available_port():
    for port in range(5560, 5584, 2):
        sockets = [socket.socket(), socket.socket()]
        try:
            sockets[0].bind(("127.0.0.1", port))
            sockets[1].bind(("127.0.0.1", port + 1))
            return port
        except OSError:
            continue
        finally:
            for item in sockets:
                item.close()
    raise RuntimeError("No free emulator port pair")


def start(root, state):
    if "serial" in state:
        raise RuntimeError("This run already has a device attempt; retain it and prepare a fresh run")
    env = environment(state, root)
    checked([tool(state, "cmdline-tools/latest/bin/avdmanager"), "create", "avd",
             "--name", state["avd_name"], "--package", state["image"],
             "--path", root / "avd/device.avd", "--device", "pixel"], env,
            root / "avd-create.log", input_text="no\n")
    config = root / "avd/device.avd/config.ini"
    settings = dict(line.split("=", 1) for line in config.read_text().splitlines() if "=" in line)
    settings.update({"hw.keyboard": "yes", "hw.ramSize": "2048", "hw.lcd.width": "480",
                     "hw.lcd.height": "800", "hw.lcd.density": "160", "hw.cpu.ncore": "2"})
    config.write_text("".join(f"{key}={value}\n" for key, value in settings.items()))
    port = available_port()
    state["serial"] = f"emulator-{port}"
    command = [str(tool(state, "emulator/emulator")), "-avd", state["avd_name"],
               "-port", str(port), "-no-window", "-no-audio", "-no-boot-anim",
               "-no-snapshot", "-gpu", "swiftshader_indirect", "-accel", "on"]
    with (root / "emulator.log").open("w") as stream:
        process = subprocess.Popen(command, env=env, stdout=stream, stderr=stream,
                                   start_new_session=True)
    state["pid"] = process.pid
    state["emulator_command"] = command
    save(root, state)
    deadline = time.monotonic() + 180
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise RuntimeError(f"Emulator exited {process.returncode}; see {root / 'emulator.log'}")
        result = adb(state, "shell", "getprop", "sys.boot_completed")
        if result.returncode == 0 and result.stdout.strip() == "1":
            assert_device(state)
            state["fingerprint"] = adb(state, "shell", "getprop", "ro.build.fingerprint").stdout.strip()
            state["booted"] = True
            save(root, state)
            print(json.dumps(state, indent=2))
            return
        time.sleep(1)
    raise RuntimeError(f"Boot deadline exceeded; retain logs and clean up {root}")


def install(root, state, variant):
    assert_device(state)
    build_info = state["builds"][variant]
    apk = Path(build_info["apk"])
    if digest(apk) != build_info["sha256"]:
        raise RuntimeError("APK hash no longer matches the recorded build")
    log = root / "install.log"
    checked([tool(state, "platform-tools/adb"), "-s", state["serial"],
             "install", "-r", apk], environment(state, root), log)
    state["installed"] = dict(build_info, variant=variant)
    save(root, state)
    print(f"Installed {build_info['sha256']} on {state['serial']}; app data was retained")


def cleanup(root, state):
    if state.get("serial"):
        result = adb(state, "get-state")
        if result.returncode == 0:
            assert_device(state)
            result = adb(state, "emu", "kill")
            if result.returncode:
                raise RuntimeError("Owned emulator refused shutdown")
            deadline = time.monotonic() + 30
            while time.monotonic() < deadline and adb(state, "get-state").returncode == 0:
                time.sleep(0.5)
            if adb(state, "get-state").returncode == 0:
                raise RuntimeError("Emulator is still running; data retained")
        deadline = time.monotonic() + 15
        while True:
            process = execute(["ps", "-p", str(state["pid"]), "-o", "command="])
            if process.returncode != 0 or not process.stdout.strip():
                break
            if time.monotonic() >= deadline:
                raise RuntimeError("Recorded process still exists; inspect it before deleting device state")
            time.sleep(0.5)
    for name in ("avd", "android-user"):
        path = root / name
        if path.is_symlink():
            raise RuntimeError("Refusing cleanup through a symlink")
        if path.exists():
            shutil.rmtree(path)
    state["cleaned"] = True
    save(root, state)
    print("Owned emulator stopped and device state removed; builds, logs and evidence retained")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("prepare", "start", "install", "status", "cleanup"))
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--sdk", default=os.environ.get("ANDROID_HOME", str(Path.home() / "Library/Android/sdk")))
    parser.add_argument("--java-home", default=os.environ.get("JAVA_HOME", "/Applications/Android Studio.app/Contents/jbr/Contents/Home"))
    parser.add_argument("--api", default="34")
    parser.add_argument("--build-tools", default="34.0.0")
    parser.add_argument("--image", default="system-images;android-34;google_apis;arm64-v8a")
    parser.add_argument("--variant", choices=("baseline", "seeded"), default="seeded")
    args = parser.parse_args()
    root = args.run_dir.expanduser().resolve()
    if args.action == "prepare":
        prepare(args, root)
        return
    state = load(root)
    if args.action == "start":
        start(root, state)
    elif args.action == "install":
        install(root, state, args.variant)
    elif args.action == "cleanup":
        cleanup(root, state)
    else:
        assert_device(state)
        print(json.dumps(state, indent=2))


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError, RuntimeError, subprocess.TimeoutExpired) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        sys.exit(1)
