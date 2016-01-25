"""Tweak the Apache .conf files to suit the current environment
"""
import os, sys
import glob
import shutil

import win32con
import win32gui
import win32process

def get_hwnds_for_title(title):
    def callback(hwnd, hwnds):
        if win32gui.IsWindowVisible(hwnd) and win32gui.IsWindowEnabled(hwnd):
            if title in win32gui.GetWindowText(hwnd):
                hwnds.append(hwnd)
        return True

    hwnds = []
    win32gui.EnumWindows(callback, hwnds)
    return hwnds

def kill_running_apache():
    for hwnd in get_hwnds_for_title("apache\\bin\\httpd.exe"):
        win32gui.SendMessage(hwnd, win32con.WM_CLOSE, 0, 0)

def reconfigure_conf(master_filepath, substitutions):
    conf_filepath = master_filepath[:-(len(".master"))]
    print("Reconfigure", master_filepath, "to", os.path.basename(conf_filepath))
    with open(master_filepath, "r") as inf:
        with open(conf_filepath, "w") as outf:
            outf.write(inf.read().format(**substitutions))

def reconfigure_confs(conf_dirpath, substitutions):
    for master_filepath in glob.glob(os.path.join(conf_dirpath, "*.conf.master")):
        reconfigure_conf(master_filepath, substitutions)

def enable_htaccess(htaccess_dirpath):
    htmaster_filepath = os.path.join(htaccess_dirpath, ".htaccess.template")
    htaccess_filepath = os.path.join(htaccess_dirpath, ".htaccess")
    if not os.path.exists(os.path.join(htaccess_dirpath, ".htaccess")):
        shutil.copy(htmaster_filepath, htaccess_filepath)

def main(branch="dev"):
    kill_running_apache()

    here = os.path.dirname(__file__)
    location = os.path.join(here, "..")
    substitutions = {
        #
        # The apache.conf format itself uses {} for substitution (in log entries)
        # For q-and-d'ness, just replace those by their original selves
        #
        "Referer" : "{Referer}",
        "User-Agent" : "{User-Agent}",
        "weekdaymasses" : location.replace("\\", "/"),
        "branch" : branch
    }
    reconfigure_confs(os.path.join(here, "conf"), substitutions)
    reconfigure_confs(os.path.join(here, "conf", "extra"), substitutions)
    enable_htaccess(os.path.join(location, branch))

if __name__ == '__main__':
    main(*sys.argv[1:])
