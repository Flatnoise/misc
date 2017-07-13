#!/usr/bin/python

# A script to backup content from remote windows PC to linux fileserver using rsync
# The script is creating 'current' dir with latest backup
# Previously created 'current' dir is renaming to dir like 'previous-'
# Notice: date in the end on 'previous-' dir DO NOT mean the date of backup!
#		this is the date when the 'current' directory was rewritten!
# i.e. 'previous-2017-03-02' means that 'current' dir from 2017-03-01 was renamed 2017-03-02

# written by Snownoise
# 2017-07-13

from subprocess import check_output, STDOUT, CalledProcessError
from datetime import datetime
from backup_pc_config import *
import inspect
import os


# Adds timestamp to text
def log_str(text):
    logtime = datetime.now()
    return str(logtime) + "\t" + str(text) + "\n"


with open(stng_log_d, "a") as log:
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
	
	# Performing daily backup
	if fl_mount:
		try:
			# Moving latest dir to another
			currDate = datetime
			newPrevDir = "previous-" + currDate.now().strftime("%Y-%m-%d")	

			# Check for backup list file
			if not os.path.isfile(stng_bckp_list_d):
				log.write(log_str("E> backup list file is not exists"))
				raise Exception("Backup list file is not exists")
			
			# Check if previous dir is already exists
			if os.path.isdir(os.path.join(stng_bckp_dir, newPrevDir)):
				log.write(log_str("E> directory is already exists: " + newPrevDir))
				raise Exception("Directory is already exists")
			
			# Check if current dir is already exists
			if os.path.isdir(os.path.join(stng_bckp_dir, "current")):
				# Rename current to previous if exists
				os.rename(os.path.join(stng_bckp_dir, "current"), os.path.join(stng_bckp_dir, newPrevDir))
				log.write(log_str("I> renamed current to: " + newPrevDir))
			else:
				# Create empty previous dir for rsync if not exists ('fresh start' case)
				if not os.path.isdir(os.path.join(stng_bckp_dir, newPrevDir)):
					os.mkdir(os.path.join(stng_bckp_dir, newPrevDir))
					log.write(log_str("I> created empty previous dir: " + newPrevDir))


			# Create new current dir
			os.mkdir(os.path.join(stng_bckp_dir, "current"))
			log.write(log_str("I> created new current dir"))
				
			rsync = ["rsync",
				"-vrt",
				"--files-from="+stng_bckp_list_d,
				"--exclude-from="+stng_exclude_list,
				"--link-dest="+str(os.path.join(stng_bckp_dir, newPrevDir)),
				"/",
				str(os.path.join(stng_bckp_dir, "current"))]
				
			
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



