import paramiko
from tkinter import messagebox

class sshClient(object):
    def __init__(self):
        self.client=paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    def __del__(self):
        self.Close()

    def Connect(self, host, port, username, password):
        try:
            self.client.close()
        except:
            pass
        self.Connected=True
        try:
            # print(host, port, username, password)
            self.client.connect(host, port=port, username=username, password=password, timeout=5)
        except:
            messagebox.showerror("SSH失败",f"连接服务器 {host}:{port} 失败！")
            self.Connected=False

    def Close(self):
        self.client.close()

    def Upload(self, source, dest):
        print(f"Upload({source},{dest})")
        try:
            self.client.open_sftp().put(source, dest)
        except:
            messagebox.showerror("SSH失败", f"上传文件{source}至{dest}时失败！")
            return False
        return True

    def Download(self, source, dest):
        print(f"Download({source},{dest})")
        try:
            self.client.open_sftp().get(source, dest)
        except:
            messagebox.showerror("SSH失败", f"下载文件{source}至{dest}时失败！")
            return False
        return True