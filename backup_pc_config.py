# change values below according to your system

# username on windows system
stng_smb_username = "username"

# password on windows system
stng_smb_password = "password"

# path to your SMB share
stng_smb_path = "//home-pc/bckp_directory$"		

# path to you SMB share mountpoint on linux server
stng_smp_mntpoint = "/mnt/backup_share"				

# backup folder on linux server
stng_bckp_dir = "/home/backupuser/backups/" 

# file with list of directories for daily backup. Use linux path from your mountpoint
stng_bckp_list_d = "/home/backupuser/backups/backup_list.txt"

# file with list of directories for monthly backup. Use linux path from your mountpoint
stng_bckp_list_m = "/home/backupuser/backups/backup_list_monthly.txt"

# file with list of files to exclude
stng_exclude_list = "/home/backupuser/backups/exclude_list.txt"

# path to logfile for daily script
stng_log_d = "/home/backupuser/backups/backup_pc_daily.log"

# path to logfile for monthly script
stng_log_m = "/home/backupuser/backups/backup_pc_monthly.log"