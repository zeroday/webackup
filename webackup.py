import ftputil
import os.path
dir_dest = '/tmp/ftptest/'
ftp = ftputil.FTPHost('ftp.microsoft.com','anonymous','')
recursive = ftp.walk("MISC",topdown=True,onerror=None)
for root,dirs,files in recursive:
    for fname in files:
        fpath = ftp.path.join(root, fname)
        print fname, fpath
        if ftp.path.isfile(fpath):
            ftp.download(fpath, os.path.join(dir_dest, fname), 'b')
ftp.close
