import ftputil
import os.path

# root directory for local host
root_ldir = '/tmp/ftptest/'
# root directory for ftp host
root_fdir = 'MISC'

#connect to the FTP server
ftp = ftputil.FTPHost('ftp.microsoft.com','anonymous','')

# gather the remote file structure
recursive = ftp.walk(root_fdir,topdown=True,onerror=None)


for root,dirs,files in recursive:
    for fname in files:
        fpath = ftp.path.join(root, fname)
        lpath = ftp.path.dirname(fpath)
        dest_dir = os.path.join(root_ldir, lpath)

        # TODO if file is in exclude list skip

        # if the local directory doesn't exist make it
        try:
            os.stat(dest_dir)
        except:
            os.makedirs(dest_dir)

        # download the file in the target directory
        try:
             if ftp.path.isfile(fpath):
                target = os.path.join(dest_dir, fname)
                ftp.download_if_newer(fpath,target, 'b')
        except IOError, obj:
            raise IOError("%s" % (obj.strerror))

ftp.close
