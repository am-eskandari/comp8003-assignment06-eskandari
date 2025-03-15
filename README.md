# **File Integrity Monitoring System (FIM)**

## **COMP 8003 - Assignment 6**

---

## **Table of Contents**

- [Introduction](#introduction)
- [How It Works](#how-it-works)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Automating Integrity Checks with Cron](#automating-integrity-checks-with-cron)

---

## **Introduction**

This **File Integrity Monitoring (FIM) System** is a security tool designed to detect unauthorized modifications in
critical system files within the `/etc` directory. The program monitors changes by computing **SHA-256 hashes**, storing
them as a **baseline**, and comparing them against the **current state** of the files. If any discrepancies are found,
they are logged and reported.

This project is part of **COMP 8003 - Assignment 6** and demonstrates key concepts in **system security, scripting, and
automated monitoring**.

---

## **How It Works**

1. **Baseline Creation (`--baseline`)**:
    - Computes **SHA-256 hashes** for all files in `/etc` (excluding symbolic links and lock files).
    - Stores these hashes in `logs/etc_hashes.txt` for future comparisons.

2. **Integrity Check (`--check`)**:
    - Computes current hashes for all monitored files.
    - Compares them against the **baseline** using `diff`.
    - Detects **modified, new, or deleted** files and logs them to `logs/integrity_report.log`.

3. **Report Viewing (`--report`)**:
    - Displays the latest integrity check report.

4. **Clearing Reports (`--clear-report`)**:
    - Deletes the integrity report to free up storage.

5. **Automation via Cron**:
    - Can be **scheduled to run periodically** using `cron`, ensuring continuous monitoring.

---

## **Features**

✅ **Monitors file integrity** using **SHA-256 hashing**  
✅ **Detects file modifications, additions, and deletions**  
✅ **Logs unauthorized changes** in a structured report  
✅ **Handles symbolic links and permission errors gracefully**  
✅ **Automates integrity checks via `cron`**

---

## **Installation**

### **Prerequisites**

- **Arch Linux / EndeavourOS / Ubuntu / Fedora / FreeBSD**
- **Bash shell**
- **Cron (for automation)**
- **Root or sudo access** (for system-wide monitoring)

### **Cloning the Repository**

```bash
git clone https://github.com/your-repo-url/comp8003-assignment06-eskandari.git
cd comp8003-assignment06-eskandari
```

### **Setting Up the Script**

Ensure the script has **execute permissions**:

```bash
chmod +x src/fim.sh
```

---

## **Usage**

The program provides the following command-line options:

### **Generating a Baseline**

```bash
sudo ./src/fim.sh --baseline
```

Creates a baseline of system file hashes.

### **Checking for Unauthorized Modifications**

```bash
sudo ./src/fim.sh --check
```

Compares files against the baseline and logs any changes.

### **Viewing the Integrity Report**

```bash
sudo ./src/fim.sh --report
```

Displays detected changes.

### **Clearing the Integrity Report**

```bash
sudo ./src/fim.sh --clear-report
```

Deletes the previous integrity report.

---

## **Automating Integrity Checks with Cron**

To run **automatic integrity checks** every 5 minutes:

1. **Add a cron job:**
   ```bash
   (crontab -l 2>/dev/null; echo "*/5 * * * * /home/amir/Documents/Repos/comp8003-assignment06-eskandari/src/fim.sh --check >> /home/amir/Documents/Repos/comp8003-assignment06-eskandari/logs/cron.log 2>&1") | crontab -
   ```
2. **Restart Cron Service:**
   ```bash
   sudo systemctl restart cronie  # Arch Linux
   ```

To manually trigger the **cron job immediately** for testing:

```bash
/home/amir/Documents/Repos/comp8003-assignment06-eskandari/src/fim.sh --check
```

---
