#!/bin/bash

# Define paths
REPO_DIR="$(cd "$(dirname "$0")" && pwd)/.."  # Ensure it resolves to project root
LOG_DIR="$REPO_DIR/logs"

BASELINE_FILE="$LOG_DIR/etc_hashes.txt"
CURRENT_FILE="/tmp/current_hashes.txt"
REPORT_FILE="$LOG_DIR/integrity_report.log"
INTEGRITY_LOG="$LOG_DIR/integrity_monitor.log"

# Ensure log directory exists
mkdir -p "$LOG_DIR"

log_event() {
    local level="$1"
    local message="$2"
    local timestamp
    timestamp=$(date +"%Y-%m-%d %H:%M:%S")
    local log_message="[$timestamp] [$level] $message"

    # Append to log file
    echo "$log_message" >> "$INTEGRITY_LOG"

    # Print alerts to console
    if [[ "$level" == "ERROR" || "$level" == "ALERT" ]]; then
        echo -e "\033[91m🚨 ALERT: $message\033[0m" >&2
    else
        echo "$log_message"
    fi
}

generate_baseline() {
    echo "Generating baseline hashes for /etc directory..."
    log_event "INFO" "Generating baseline hashes for /etc directory."

    # Hash all files in /etc, excluding symlinks and lock files
    find /etc -type f ! -name "*.lock" ! -type l -exec sha256sum {} + | sort > "$BASELINE_FILE" 2>/dev/null

    log_event "INFO" "Baseline saved to $BASELINE_FILE"
    echo "Baseline saved to $BASELINE_FILE"
}

check_integrity() {
    echo "🔍 Checking file integrity..."
    log_event "INFO" "Checking file integrity."

    # Ensure baseline exists
    if [[ ! -f "$BASELINE_FILE" ]]; then
        log_event "ERROR" "Baseline file not found. Run --baseline first."
        echo "Error: Baseline file not found. Run --baseline first." >&2
        exit 1
    fi

    # Generate current hashes for comparison
    find /etc -type f ! -name "*.lock" ! -type l -exec sha256sum {} + | sort > "$CURRENT_FILE" 2>/dev/null

    # Compare baseline with current hashes using diff
    diff_output=$(diff -u "$BASELINE_FILE" "$CURRENT_FILE")

    # Initialize lists for changes
    modified_files=()
    new_files=()
    deleted_files=()

    while IFS= read -r line; do
        if [[ "$line" =~ ^\+[^+] ]]; then
            filepath=$(echo "$line" | awk '{print $2}')
            if grep -q "$filepath" "$BASELINE_FILE"; then
                modified_files+=("$filepath")  # File existed before → Mark as modified
            else
                new_files+=("$filepath")  # File is entirely new
            fi
        elif [[ "$line" =~ ^-[^-] ]]; then
            filepath=$(echo "$line" | awk '{print $2}')
            if ! grep -q "$filepath" "$CURRENT_FILE"; then
                deleted_files+=("$filepath")  # File was removed
            fi
        fi
    done <<< "$diff_output"

    # Print summary
    echo -e "\n🚨 Integrity Check Summary 🚨" | tee "$REPORT_FILE"

    if [[ ${#modified_files[@]} -gt 0 ]]; then
        echo "🟠 Modified Files:" | tee -a "$REPORT_FILE"
        for file in "${modified_files[@]}"; do
            echo "    🔸 $file" | tee -a "$REPORT_FILE"
        done
    fi
    if [[ ${#new_files[@]} -gt 0 ]]; then
        echo "🟢 New Files:" | tee -a "$REPORT_FILE"
        for file in "${new_files[@]}"; do
            echo "    🟩 $file" | tee -a "$REPORT_FILE"
        done
    fi
    if [[ ${#deleted_files[@]} -gt 0 ]]; then
        echo "🔴 Deleted Files:" | tee -a "$REPORT_FILE"
        for file in "${deleted_files[@]}"; do
            echo "    ❌ $file" | tee -a "$REPORT_FILE"
        done
    fi

    if [[ ${#modified_files[@]} -eq 0 && ${#new_files[@]} -eq 0 && ${#deleted_files[@]} -eq 0 ]]; then
        log_event "INFO" "No unauthorized changes detected."
        echo "✅ No unauthorized changes detected."
    else
        log_event "ALERT" "Unauthorized changes detected!"
        log_event "ALERT" "Modified Files: ${modified_files[*]}"
        log_event "ALERT" "New Files: ${new_files[*]}"
        log_event "ALERT" "Deleted Files: ${deleted_files[*]}"
    fi
}

display_report() {
    if [[ -f "$REPORT_FILE" ]]; then
        echo "=== Integrity Report ==="
        cat "$REPORT_FILE"
    else
        echo "No integrity report found."
    fi
}

clear_report() {
    rm -f "$REPORT_FILE"
    echo "Integrity report cleared."
}

# Handle command-line arguments
case "$1" in
    --baseline) generate_baseline ;;
    --check) check_integrity ;;
    --report) display_report ;;
    --clear-report) clear_report ;;
    *)
        echo "Usage: $0 --baseline | --check | --report | --clear-report"
        exit 1
        ;;
esac
