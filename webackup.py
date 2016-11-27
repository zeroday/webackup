import ftputil
import os.path
import yaml
import re

config = yaml.load(file("config.yml"))
print config

# root directory for local host
root_ldir = config['root_ldir']
print root_ldir

# root directory for ftp host
root_fdir = config['root_fdir']
print root_fdir

# directories to exclude
excluded_dirs = config['excluded_dirs']
print excluded_dirs

excluded_files = config['excluded_files']
print excluded_files

excluded_filetypes = ['\.zip', '\.tar', '\.tar\.gz', '\.gz', '\.rar']
print excluded_filetypes

# ftp server credentials
ftp_host = config['ftp_host']
ftp_user = config['ftp_user']
ftp_pass = config['ftp_pass']

print ftp_host, ftp_user, ftp_pass

# connect to the FTP server
ftp = ftputil.FTPHost(ftp_host, ftp_user, ftp_pass)
print ftp
# gather the remote file structure
recursive = ftp.walk(root_fdir, topdown=True, onerror=None)
print recursive

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


def download_file(root_ldir, fpath, fname, lpath, dest_dir):
    # if the directory doesn't exist locally then create it
    # TODO ignore softlinks
    make_directory = False
    if dest_dir.startswith('/'):
        dest_dir = dest_dir[1:]

    try:
        os.stat(dest_dir)
    except:
        make_directory = True

    if make_directory:
        try:
            os.makedirs(os.path.join(root_ldir, lpath, dest_dir))
        except:
            return False
        
    print(root_ldir, lpath, dest_dir)
    
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
    except ftputil.error.FTPOSError, exc:
        print exc


for root,dirs,files in recursive:
    for fname in files:
        fpath = ftp.path.join(root, fname)
        lpath = ftp.path.dirname(fpath)
        dest_dir = os.path.join(root_ldir, lpath)

        print fname, fpath, lpath, dest_dir

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
            print lpath
            continue
        else:
            print(root_ldir, fpath, fname, lpath, dest_dir)
            download_file(root_ldir, fpath, fname, lpath, dest_dir)

ftp.close
