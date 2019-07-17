#!/usr/bin/python

# A script to backup content from remote windows PC to linux fileserver using rsync
# The script is creating 'current' dir with latest backup
# Previously created 'current' dir is renaming to dir like 'previous-'

# written by Snownoise
# 2017-07-13
# 2019-07-17

from subprocess import check_output, STDOUT, CalledProcessError
from datetime import datetime
from backup_pc_config import *
import logging
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)-15s %(levelname)-10s %(message)s', filename=stng_log_d, filemode="a")
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

# Performing daily backup
if fl_mount:
    try:
        # Moving latest dir to another
        currDate = datetime
        newPrevDir = 'backup-{}-moved-{}'.format(
            datetime.utcfromtimestamp(os.path.getctime(os.path.join(stng_bckp_dir, "current"))).strftime('%Y-%m-%d'),
            currDate.now().strftime("%Y-%m-%d"))

        # Check for backup list file
        if not os.path.isfile(stng_bckp_list_d):
            logging.error("Backup list file is not exists")
            raise Exception("Backup list file is not exists")

        # Check if previous dir is already exists
        if os.path.isdir(os.path.join(stng_bckp_dir, newPrevDir)):
            logging.error("Directory is already exists: {}".format(newPrevDir))
            raise Exception("Directory is already exists")

        # Check if current dir is already exists
        if os.path.isdir(os.path.join(stng_bckp_dir, "current")):
            # Rename current to previous if exists
            os.rename(os.path.join(stng_bckp_dir, "current"), os.path.join(stng_bckp_dir, newPrevDir))
            logging.info("Renamed current dir to {}".format(newPrevDir))
        else:
            # Create empty previous dir for rsync if not exists ('fresh start' case)
            if not os.path.isdir(os.path.join(stng_bckp_dir, newPrevDir)):
                os.mkdir(os.path.join(stng_bckp_dir, newPrevDir))
                logging.info("Created empty previous dir: {}".format(newPrevDir))


        # Create new current dir
        os.mkdir(os.path.join(stng_bckp_dir, "current"))
        logging.info("Created new current dir")

        rsync = ["rsync",
            "-vrt",
            "--files-from="+stng_bckp_list_d,
            "--exclude-from="+stng_exclude_list,
            "--link-dest="+str(os.path.join(stng_bckp_dir, newPrevDir)),
            "/",
            str(os.path.join(stng_bckp_dir, "current"))]


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



