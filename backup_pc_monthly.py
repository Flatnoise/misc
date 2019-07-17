#!/usr/bin/python

# A script to create monthly snapshot using rsync
# This script is an addition to backup_pc_daily.py script
# This script is creating 'monthly' dir with latest backup based on 'current' dir backup
# Not really a script to create monthly backups!
# I need this only to offsite backup 'monthly' dir by another backup solution

# written by Snownoise
# 2017-07-13
# 2019-07-17

from subprocess import check_output, STDOUT, CalledProcessError
from datetime import datetime
from shutil import rmtree
from backup_pc_config import *
import logging
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)-15s %(levelname)-10s %(message)s', filename=stng_log_m, filemode="a")
logging.info("\nScript started")

# Listing all mounted shares
all_mounts = str(check_output("mount"))

# Check if resource already mounted, unmount if mounted
if all_mounts.find(stng_smb_path) != -1:
    logging.info("{} is already mounted, unmounting".format(stng_smp_mntpoint))
    try:
        umount_res = check_output(["umount", stng_smp_mntpoint], stderr=STDOUT)
        fl_mount = False
    except (CalledProcessError, e):
        logging.error(e.output.decode("utf-8"))
    

# Create arguments for mount command
mount_args = "mount", "-t", "cifs", "-o", "username=" + stng_smb_username + ",password=" + stng_smb_password + ",iocharset=utf8", stng_smb_path, stng_smp_mntpoint

# Mounting share
try:
    mount_res = check_output(mount_args, stderr=STDOUT)
    logging.info("Resource {} mounted".format(stng_smb_path))
    fl_mount = True
except (CalledProcessError, e):
    fl_mount = False
    logging.error(e.output.decode("utf-8"))

# Performing monthly backup
if fl_mount:
    try:
        # Removing monthly backup dir completely if present
        if os.path.isdir(os.path.join(stng_bckp_dir, "monthly")):
            rmtree(os.path.join(stng_bckp_dir, "monthly"))
            logging.info("Removing monthly dir")
    
        # Create empty monthly dir
        os.mkdir(os.path.join(stng_bckp_dir, "monthly"))
        logging.info("Created empty monthly dir")
            
        # Check for backup list file
        if not os.path.isfile(stng_bckp_list_m):
            logging.error("Backup list file is not exists")
            raise Exception("Backup list file is not exists")
        
        # Check if current dir is already exists
        if not os.path.isdir(os.path.join(stng_bckp_dir, "current")):
            logging.error("Current dir is not found")
            raise Exception("Current dir is not found")

        rsync = ["rsync",
            "-vrt",
            "--files-from="+stng_bckp_list_m,
            "--exclude-from="+stng_exclude_list,
            "--link-dest="+str(os.path.join(stng_bckp_dir, "current")),
            "/",
            str(os.path.join(stng_bckp_dir, "monthly"))]
            
        
        rsync_res = check_output(rsync, stderr=STDOUT)
        logging.info("Backup performed {}".format(rsync_res))
    except CalledProcessError as e:
        if e.returncode == 23 or e.returncode == 24:
            logging.warning(e.output.decode("utf-8"))
            logging.info("Backup somehow performed")
        else:
            logging.error(e.output.decode("utf-8"))
    except Exception:
        pass
        
    
    # Unmount share
    try:
        umount_res = check_output(["umount", stng_smp_mntpoint], stderr=STDOUT)
        logging.info("Share {} unmounted \n\n\n".format(stng_smp_mntpoint))
    except (CalledProcessError, e):
        logging.error(e.output.decode("utf-8"))



