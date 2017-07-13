#!/usr/bin/python

# A script to create monthly snapshot using rsync
# This script is an addition to backup_pc_daily.py script
# This script is creating 'monthly' dir with latest backup based on 'current' dir backup
# Not really a script to create monthly backups!
# I need this only to offsite backup 'monthly' dir by another backup solution

# written by Snownoise
# 2017-07-13

from subprocess import check_output, STDOUT, CalledProcessError
from datetime import datetime
from shutil import rmtree
from backup_pc_config import *
import inspect
import os


# Adds timestamp to text
def log_str(text):
    logtime = datetime.now()
    return str(logtime) + "\t" + str(text) + "\n"
	
with open(stng_log, "a") as log:
	log.write("\n")
	# Listing all mounted shares
	all_mounts = check_output("mount")

	# Check if resource already mounted, unmount if mounted
	if all_mounts.find(stng_smb_path) != -1:
		log.write(log_str("I> " + stng_smp_mntpoint + " is already mounted, unmounting"))
		try:
			umount_res = check_output(["umount", stng_smp_mntpoint], stderr=STDOUT)
			fl_mount = False
		except CalledProcessError, e:
			log.write(log_str("E> " + e.output))
		
		

	# Create arguments for mount command
	mount_args = "mount", "-t", "cifs", "-o", "username=" + stng_smb_username + ",password=" + stng_smb_password + ",iocharset=utf8", stng_smb_path, stng_smp_mntpoint

	#mounting share
	try:
		mount_res = check_output(mount_args, stderr=STDOUT)
		log.write(log_str("I> Resource " + stng_smb_path + " mounted"))
		fl_mount = True
	except CalledProcessError, e:
		fl_mount = False
		log.write(log_str("E> " + e.output))
	
	# Performing monthly backup
	if fl_mount:
		try:
			# Removing monthly backup dir completely if present
			if os.path.isdir(os.path.join(stng_bckp_dir, "monthly")):
				rmtree(os.path.join(stng_bckp_dir, "monthly"))
				log.write(log_str("I> removing monthly dir"))
		
			# Create empty monthly dir
			os.mkdir(os.path.join(stng_bckp_dir, "monthly"))
			log.write(log_str("I> created empty monthly dir"))
				
			# Check for backup list file
			if not os.path.isfile(stng_bckp_list_m):
				log.write(log_str("E> backup list file is not exists"))
				raise Exception("Backup list file is not exists")
			
			# Check if current dir is already exists
			if not os.path.isdir(os.path.join(stng_bckp_dir, "current")):
				log.write(log_str("E> current dir is not found"))
				raise Exception("Current dir is not found")

			rsync = ["rsync",
				"-vrt",
				"--files-from="+stng_bckp_list_m,
				"--exclude-from="+stng_exclude_list,
				"--link-dest="+str(os.path.join(stng_bckp_dir, "current")),
				"/",
				str(os.path.join(stng_bckp_dir, "monthly"))]
				
			
			rsync_res = check_output(rsync, stderr=STDOUT)
			log.write(log_str("I> Backup performed " + rsync_res))
		except CalledProcessError, e:
			log.write(log_str("E> " + e.output))
		except Exception:
			pass
			
		
		# Unmount share
		try:
			#pass
			umount_res = check_output(["umount", stng_smp_mntpoint], stderr=STDOUT)
			log.write(log_str("I> Share " + stng_smp_mntpoint + " unmounted"))
		except CalledProcessError, e:
			log.write(log_str("E> " + e.output))
	
	log.write(log_str("I> Finishing script"))
	log.close()



