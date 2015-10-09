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
excluded_files = config['excluded_files']
excluded_filetypes = ['\.zip', '\.tar', '\.tar\.gz', '\.gz', '\.rar']

# ftp server credentials
ftp_host = config['ftp_host']
ftp_user = config['ftp_user']
ftp_pass = config['ftp_pass']

# connect to the FTP server
ftp = ftputil.FTPHost(ftp_host, ftp_user, ftp_pass)

# gather the remote file structure
recursive = ftp.walk(root_fdir, topdown=True, onerror=None)

def exclude_this_directory(target):
    global excluded_dirs

    if not excluded_dirs:
        return False

    for relative_dir in excluded_dirs:
        # it is assumed that all subdirectories are excluded
        excluded_dir = ftp.path.join(root_fdir, relative_dir)
        if (re.match(excluded_dir, target)):
            print("excluding %s" % target)
            return True
    return False

def exclude_this_filetype(target):
    # by default let's not download zip, tar.gz, rar
    global excluded_filetypes

    for filetype in excluded_filetypes:
        pattern = ".*%s$" % filetype
        if (re.match(pattern, target)):
            print("excluding %s on pattern %s" % (target, pattern))
            return True
    return False

def exclude_this_file(target):
    # by default let's not download zip, tar.gz, rar
    global excluded_files

    if not excluded_files:
        return False

    for excluded_file in excluded_files:
        excluded_file = "%s" % excluded_file
        if (re.match(excluded_file, target)):
            print(("(excluding %s" % target))
            return True
    return False


def download_file(root_ldir, path, fname, lpath, dest_dir):
    # if the directory doesn't exist locally then create it
    # TODO directory MUST be created in local root
    try:
        os.stat(dest_dir)
    except:
        os.makedirs(os.path.join(root_ldir, dest_dir))
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
    except ftputil.ftp_error.FTPOSError, exc:
        print str(exc)
    except Error, e:
        print "Bad thing happened: %s occured" % e

for root,dirs,files in recursive:
    for fname in files:
        # exclude file if found in excluded_files
        if exclude_this_filetype(fname):
            continue
        elif exclude_this_file(fname):
            continue
        else:
            fpath = ftp.path.join(root, fname)
            lpath = ftp.path.dirname(fpath)
            dest_dir = os.path.join(root_ldir, lpath)

        # exclude the directory if it is found in excluded_dirs
        if exclude_this_directory(lpath):
            continue
        else:
            download_file(root_ldir, fpath, fname, lpath, dest_dir)

ftp.close
