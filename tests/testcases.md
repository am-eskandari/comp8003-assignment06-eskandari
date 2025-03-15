# COMP 8003 - Assignment 6

## Bulk Test Commands

```bash
echo "Running Test 1: No arguments (Expect Fail)"
sudo ./fim.sh
echo "--------------------------------------------------"

echo "Running Test 2: Invalid argument (--invalid) (Expect Fail)"
sudo ./fim.sh --invalid
echo "--------------------------------------------------"

echo "Running Test 3: Run --baseline on first execution (Expect Pass)"
sudo rm -f ~/Documents/Repos/comp8003-assignment06-eskandari/logs/etc_hashes.txt
sudo ./fim.sh --baseline
echo "--------------------------------------------------"

echo "Running Test 4: Run --check without baseline existing (Expect Fail)"
sudo rm -f ~/Documents/Repos/comp8003-assignment06-eskandari/logs/etc_hashes.txt
sudo ./fim.sh --check
echo "--------------------------------------------------"

echo "Running Test 5: Run --report before any checks (Expect Fail)"
sudo rm -f ~/Documents/Repos/comp8003-assignment06-eskandari/logs/integrity_report.log
sudo ./fim.sh --report
echo "--------------------------------------------------"

echo "Running Test 6: Run --baseline when baseline already exists (Expect Pass)"
sudo ./fim.sh --baseline
sudo ./fim.sh --baseline
echo "--------------------------------------------------"

echo "Running Test 7: Run --check when no files have changed (Expect Pass)"
sudo ./fim.sh --baseline
sudo ./fim.sh --check
echo "--------------------------------------------------"

echo "Running Test 8: Run --check after modifying a file (Expect Pass)"
sudo sed -i '1s/^/# Test modification\n/' /etc/hosts
sudo ./fim.sh --check
sudo sed -i '1d' /etc/hosts # Revert modification
echo "--------------------------------------------------"

echo "Running Test 9: Run --check after deleting a file (Expect Pass)"
sudo touch /etc/test_deleted_file.conf
sudo ./fim.sh --baseline
sudo rm /etc/test_deleted_file.conf
sudo ./fim.sh --check
echo "--------------------------------------------------"

echo "Running Test 10: Run --check after adding a new file (Expect Pass)"
sudo touch /etc/test_new_file.conf
sudo ./fim.sh --check
sudo rm /etc/test_new_file.conf
echo "--------------------------------------------------"

echo "Running Test 11: Run --check with unreadable files (permission denied) (Expect Pass)"
sudo touch /etc/test_unreadable.conf
sudo chmod 000 /etc/test_unreadable.conf
sudo ./fim.sh --check
sudo chmod 644 /etc/test_unreadable.conf
sudo rm /etc/test_unreadable.conf
echo "--------------------------------------------------"

echo "Running Test 12: Run --check with symbolic links in /etc (Expect Pass)"
sudo ln -s /etc/hosts /etc/test_symlink
sudo ./fim.sh --check
sudo rm /etc/test_symlink
echo "--------------------------------------------------"

echo "Running Test 13: Run --baseline as a non-root user (Expect Fail)"
./fim.sh --baseline
echo "--------------------------------------------------"

echo "Running Test 14: Run --check as a non-root user (Expect Fail)"
./fim.sh --check
echo "--------------------------------------------------"

echo "Running Test 15: Modify /etc file and restore before --check (Expect Pass)"
sudo cp /etc/hosts /etc/hosts.bak
sudo sed -i '1s/^/# Temporary change\n/' /etc/hosts
sudo ./fim.sh --check
sudo mv /etc/hosts.bak /etc/hosts
echo "--------------------------------------------------"

echo "Running Test 16: Run --check immediately after --baseline with no changes (Expect Pass)"
sudo ./fim.sh --baseline
sudo ./fim.sh --check
echo "--------------------------------------------------"

echo "Running Test 17: Run script via cron job and check log output (Expect Pass)"

echo "*/5 * * * * /home/amir/Documents/Repos/comp8003-assignment06-eskandari/src/fim.sh --check >>
/home/amir/Documents/Repos/comp8003-assignment06-eskandari/logs/cron.log 2>&1" | crontab -

sudo systemctl restart cronie # Use 'cronie' for Arch Linux

/home/amir/Documents/Repos/comp8003-assignment06-eskandari/src/fim.sh --check

echo "Cron job added, service restarted, and command executed immediately for testing."
echo "--------------------------------------------------"
```