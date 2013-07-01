import ftputil
import os.path
import yaml
import re

config = yaml.load(file("config.yml"))

# root directory for local host
root_ldir = config['root_ldir']

# root directory for ftp host
root_fdir = config['root_fdir']

# directories to exclude
excluded_dirs = config['excluded_dirs']

# ftp server credentials
ftp_host = config['ftp_host']
ftp_user = config['ftp_user']
ftp_pass = config['ftp_pass']

# connect to the FTP server
ftp = ftputil.FTPHost(ftp_host, ftp_user, ftp_pass)

# gather the remote file structure
recursive = ftp.walk(root_fdir,topdown=True,onerror=None)

def exclude_this_directory(target):
    for relative_dir in excluded_dirs:
        # it is assumed that all subdirectories are excluded
        excluded_dir = ftp.path.join(root_fdir, relative_dir)
        if (re.match(excluded_dir, target)):
            return True
    return False

def download_file(fpath, fname, lpath, dest_dir):
    # if the directory doesn't exist locally then create it
    try:
        os.stat(dest_dir)
    except:
        os.makedirs(dest_dir)

    # download the file into the target directory
    try:
        if ftp.path.isfile(fpath):
            target = os.path.join(dest_dir, fname)
            ftp.download_if_newer(fpath, target, 'b')
    except IOError, obj:
        print obj.strerror
        # TODO exception handler for connection time out
        # reconnect and retry the download
        # all other exceptions are logged to file
    except FTPOSError, obj:
        print obj.strerror
    

for root,dirs,files in recursive:
    for fname in files:
        fpath = ftp.path.join(root, fname)
        lpath = ftp.path.dirname(fpath)
        dest_dir = os.path.join(root_ldir, lpath)

        # exclude the directory if it is found in excluded_dirs
        if exclude_this_directory(lpath):
            continue
        else:
            download_file(fpath, fname, lpath, dest_dir)

ftp.close
