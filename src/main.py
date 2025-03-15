import argparse
import datetime
import hashlib
import os
import sys

# Define relative paths
REPO_DIR = os.path.abspath(os.path.dirname(__file__) + "/..")  # Get project root
LOG_DIR = os.path.join(REPO_DIR, "logs")  # Correct relative path


BASELINE_FILE = os.path.join(LOG_DIR, "etc_hashes.txt")
REPORT_FILE = os.path.join(LOG_DIR, "integrity_monitor.log")  # Use relative path
INTEGRITY_LOG = os.path.join(LOG_DIR, "integrity_monitor.log")  # Ensure consistency


def log_event(level, message):
    """
    Logs events with timestamps and prints critical alerts to the terminal.
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"[{timestamp}] [{level}] {message}\n"

    # Append to the log file
    with open(INTEGRITY_LOG, "a") as log_file:
        log_file.write(log_message)

    # Ensure the user sees important alerts immediately
    if level in ["ERROR", "ALERT"]:
        print(
            f"\033[91m🚨 ALERT: {message}\033[0m", file=sys.stderr
        )  # Print in RED text
    else:
        print(log_message.strip())


def parse_arguments():
    """
    Parses command-line arguments and returns the selected mode.
    """
    parser = argparse.ArgumentParser(
        description="File Integrity Monitoring System: Monitor changes in /etc directory."
    )

    parser.add_argument(
        "--baseline", action="store_true", help="Generate a baseline of file hashes."
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check file integrity against the baseline.",
    )
    parser.add_argument(
        "--report", action="store_true", help="Display the integrity report."
    )
    parser.add_argument(
        "--clear-report", action="store_true", help="Delete the integrity report."
    )

    args = parser.parse_args()

    # Ensure only one mode is selected at a time
    selected_modes = [args.baseline, args.check, args.report, args.clear_report]
    if sum(selected_modes) > 1:
        print(
            "Error: Only one operation mode can be selected at a time.", file=sys.stderr
        )
        sys.exit(1)

    # Determine mode
    if args.baseline:
        return "GENERATE_BASELINE"
    elif args.check:
        return "CHECK_INTEGRITY"
    elif args.report:
        return "DISPLAY_REPORT"
    elif args.clear_report:
        return "CLEAR_REPORT"
    else:
        print(
            "Error: No valid operation mode provided. Use --baseline, --check, --report, or --clear-report.",
            file=sys.stderr,
        )
        sys.exit(1)


def validate_arguments(mode):
    """
    Validates if the required files exist before executing the selected mode.
    """
    if mode == "CHECK_INTEGRITY":
        if not os.path.exists(BASELINE_FILE):
            print(
                f"Error: Baseline file '{BASELINE_FILE}' not found. Run '--baseline' first.",
                file=sys.stderr,
            )
            sys.exit(1)

    elif mode == "DISPLAY_REPORT":
        if not os.path.exists(REPORT_FILE):
            print(
                f"Error: Report file '{REPORT_FILE}' not found. Run '--check' first.",
                file=sys.stderr,
            )
            sys.exit(1)

    # Ensure log file is writable
    if not os.access(INTEGRITY_LOG, os.W_OK):
        print(
            f"Error: Cannot write to log file '{INTEGRITY_LOG}'. Check permissions.",
            file=sys.stderr,
        )
        sys.exit(1)


def hash_file(filepath):
    """
    Generates a SHA-256 hash for a given file.
    """
    try:
        with open(filepath, "rb") as f:
            hasher = hashlib.sha256()
            while chunk := f.read(4096):
                hasher.update(chunk)
        return hasher.hexdigest()
    except PermissionError:
        print(
            f"Warning: Skipping unreadable file '{filepath}' due to permission issues.",
            file=sys.stderr,
        )
        return None


def generate_baseline():
    """
    Generates SHA-256 hashes for all regular files in /etc and stores them in a baseline file.
    """
    print("Generating baseline hashes for /etc directory...")
    log_event("INFO", "Generating baseline hashes for /etc directory.")

    try:
        os.makedirs(LOG_DIR, exist_ok=True)  # Ensure log directory exists
        with open(BASELINE_FILE, "w") as baseline:
            for root, _, files in os.walk("/etc"):
                for file in files:
                    filepath = os.path.join(root, file)

                    # Skip non-regular files (sockets, devices, FIFOs)
                    if os.path.islink(filepath) or not os.path.isfile(filepath):
                        continue

                    hash_value = hash_file(filepath)
                    if hash_value:
                        baseline.write(f"{hash_value}  {filepath}\n")

        log_event("INFO", f"Baseline hashes saved to {BASELINE_FILE}")
        print(f"Baseline hashes saved to {BASELINE_FILE}")
    except Exception as e:
        log_event("ERROR", f"Error writing baseline file: {e}")
        print(f"Error writing baseline file: {e}", file=sys.stderr)
        sys.exit(1)


def check_integrity():
    """
    Compares current file hashes against the baseline to detect unauthorized changes.
    """
    print("🔍 Checking file integrity...")
    log_event("INFO", "Checking file integrity.")

    if not os.path.exists(BASELINE_FILE):
        log_event(
            "ERROR",
            f"Baseline file '{BASELINE_FILE}' not found. Run '--baseline' first.",
        )
        sys.exit(1)

    # Load baseline hashes
    baseline_hashes = {}
    with open(BASELINE_FILE, "r") as f:
        for line in f:
            hash_value, filepath = line.strip().split("  ", 1)
            baseline_hashes[filepath] = hash_value

    # Compute current hashes
    current_hashes = {}
    for root, _, files in os.walk("/etc"):
        for file in files:
            filepath = os.path.join(root, file)

            if os.path.islink(filepath) or not os.path.isfile(filepath):
                continue  # Skip symlinks and non-regular files

            hash_value = hash_file(filepath)
            if hash_value:
                current_hashes[filepath] = hash_value

    # Detect changes
    modified_files = []
    new_files = []
    deleted_files = []

    for filepath, old_hash in baseline_hashes.items():
        if filepath not in current_hashes:
            deleted_files.append(filepath)
        elif current_hashes[filepath] != old_hash:
            modified_files.append(filepath)

    for filepath in current_hashes:
        if filepath not in baseline_hashes:
            new_files.append(filepath)

    # Print summary to user
    print("\n🚨 Integrity Check Summary 🚨")
    if modified_files:
        print(f"🟠 Modified Files ({len(modified_files)}):")
        for f in modified_files:
            print(f"    🔸 {f}")

    if new_files:
        print(f"🟢 New Files ({len(new_files)}):")
        for f in new_files:
            print(f"    🟩 {f}")

    if deleted_files:
        print(f"🔴 Deleted Files ({len(deleted_files)}):")
        for f in deleted_files:
            print(f"    ❌ {f}")

    # Log and alert user
    log_event("INFO", f"Integrity check complete. Report saved to {REPORT_FILE}")

    if modified_files or new_files or deleted_files:
        log_event("ALERT", "Unauthorized changes detected!")
        if modified_files:
            log_event("ALERT", f"Modified Files: {', '.join(modified_files)}")
        if new_files:
            log_event("ALERT", f"New Files: {', '.join(new_files)}")
        if deleted_files:
            log_event("ALERT", f"Deleted Files: {', '.join(deleted_files)}")
    else:
        log_event("INFO", "No unauthorized changes detected.")
        print("\n✅ No unauthorized changes detected.")


def display_report():
    """
    Reads and displays the integrity report from the log file.
    """
    if not os.path.exists(REPORT_FILE):
        print(
            f"Error: Report file '{REPORT_FILE}' not found. Run '--check' first.",
            file=sys.stderr,
        )
        sys.exit(1)

    print("=== Integrity Report ===")
    with open(REPORT_FILE, "r") as report:
        print(report.read().strip())  # Print report contents


def clear_report():
    """
    Deletes the integrity report if it exists.
    """
    if os.path.exists(REPORT_FILE):
        os.remove(REPORT_FILE)
        print("Integrity report cleared.")
    else:
        print("No integrity report found.")


if __name__ == "__main__":
    mode = parse_arguments()
    validate_arguments(mode)

    if mode == "GENERATE_BASELINE":
        generate_baseline()
    elif mode == "CHECK_INTEGRITY":
        check_integrity()
    elif mode == "DISPLAY_REPORT":
        display_report()
    elif mode == "CLEAR_REPORT":
        clear_report()
    else:
        print("Unexpected error: Invalid mode.", file=sys.stderr)
        sys.exit(1)
