import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import os, json, base64, random, tempfile, zipfile, time, re
from sshClient import sshClient
from thread_func import thread_func
import AppUI
dir_sepa="------------------------文件夹------------------------"
file_sepa="-------------------------文件-------------------------"




class Application(object):
    para={"Server": "","Port": "","Username": "","Password": "","Version": "","Solver": "","Partition": "","Core": "","Account": "","WorkingDir": "","Journal": ""}

    def __init__(self):
        window=tk.Tk()
        self.UI=AppUI.UI(window, self)

        self.cfg_dir=os.path.expanduser('~')+"/.config/Slurm_Submit"
        self.read_cfg(self.cfg_dir+"/default.json")
        self.sshc=sshClient()
        self.Status("Ready")
        self.Connected=False
        self.ShowFS=True

        window.mainloop()
        self.sshc.Close()
    def open_cfg(self):
        file_path=filedialog.askopenfilename(
            title="打开配置文件", 
            initialdir=self.cfg_dir,
            filetypes=[("JSON File", "*.json"), ("Text File", "*.txt"), ("All Files", "*.*")]
        )
        if file_path:
            self.read_cfg(file_path)
            self.to_stdout(f"Read {file_path}")

    def save_cfg(self):
        file_path=filedialog.asksaveasfilename(
            title="保存配置文件", 
            initialdir=self.cfg_dir,
            initialfile="*.json",
            filetypes=[("JSON File", "*.json")]
        )
        if not file_path:
            return
        if(file_path[-5:] != ".json"):
            file_path=file_path+".json"
        self.get_para()
        data=self.para
        data["Password"]=str(base64.b64encode(data["Password"].encode('utf-8')), 'utf-8')
        with open(file_path, "w") as cfg:
            json.dump(data, cfg, indent=4)
        self.to_stdout(f"Saved {file_path}")
    

    def read_cfg(self, filepath):
        with open(filepath, "r") as cfg:
            self.para=json.load(cfg)
        self.para["Password"]=base64.b64decode(self.para["Password"]).decode("utf-8")
        self.apply_para()

    def apply_para(self): # 将cfg中的配置写入Entry
        self.Entry_Text(self.UI.Server_Entry, self.para["Server"])
        self.Entry_Text(self.UI.ServerPort_Entry, self.para["Port"])
        self.Entry_Text(self.UI.Username_Entry, self.para["Username"])
        self.Entry_Text(self.UI.Password_Entry, self.para["Password"])
        self.Entry_Text(self.UI.Ver_Combobox, self.para["Version"])
        self.Entry_Text(self.UI.Solver_Combobox, self.para["Solver"])
        self.Entry_Text(self.UI.Partition_Entry, self.para["Partition"])
        self.Entry_Text(self.UI.Processor_Spinbox, self.para["Core"])
        self.Entry_Text(self.UI.Account_Entry, self.para["Account"])
        self.Entry_Text(self.UI.WorkingDir_Entry, self.para["WorkingDir"])
        self.Entry_Text(self.UI.Journal_Entry, self.para["Journal"])
        
    def get_para(self): # 将Entry写入cfg
        self.para["Server"]=self.UI.Server_Entry.get().strip()
        self.para["Port"]=self.UI.ServerPort_Entry.get().strip()
        self.para["Username"]=self.UI.Username_Entry.get().strip()
        self.para["Password"]=self.UI.Password_Entry.get().strip()
        self.para["Version"]=self.UI.Ver_Combobox.get().strip()
        self.para["Solver"]=self.UI.Solver_Combobox.get().strip()
        self.para["Partition"]=self.UI.Partition_Entry.get().strip()
        self.para["Core"]=self.UI.Processor_Spinbox.get().strip()
        self.para["Account"]=self.UI.Account_Entry.get().strip()
        self.para["WorkingDir"]=self.UI.WorkingDir_Entry.get().strip()
        self.para["Journal"]=self.UI.Journal_Entry.get().strip()
    
    def Status(self, str):
        self.UI.statusbar["text"]=str
    def Entry_Text(self, Entry, str):
        Entry.delete(0,tk.END)
        Entry.insert(0,str)

    def stdout_cmd(self, s):
        res=None
        try:
            res=str(self.sshc.client.exec_command(s)[1].read(), encoding='utf-8')
        except:
            messagebox.showerror("SSH错误", f'尝试重新登录服务器可能解决问题\n当前服务器：{self.para["Server"]}:{self.para["Port"]}')
        if not res is None:
            res=res.strip()
        return res

    def c_cd(self, s):
        if not self.Connected:
            return
        
        self.pwd=self.stdout_cmd(f"cd \"{s}\"; pwd")
        self.Entry_Text(self.UI.CurrentDir_Path, self.pwd)


        self.Current_Dirs=self.stdout_cmd(f"find -L \"{self.pwd}\""+r" -mindepth 1 -maxdepth 1 -type d -exec basename {} \; | grep -v '^\.'").split('\n')
        self.Current_Files=self.stdout_cmd(f"find -L \"{self.pwd}\""+r" -mindepth 1 -maxdepth 1 -type f -exec basename {} \; | grep -v '^\.'").split('\n')
        self.Current_Dirs.sort(key=str.lower)
        self.Current_Dirs.insert(0, "..")
        self.Current_Files.sort(key=str.lower)

        self.UI.FileManager_Listbox.delete(0,tk.END)
        self.UI.FileManager_Listbox.insert(tk.END, dir_sepa)
        for dir in self.Current_Dirs:
            self.UI.FileManager_Listbox.insert(tk.END, dir.strip())
        self.UI.FileManager_Listbox.insert(tk.END, file_sepa)
        for file in self.Current_Files:
            self.UI.FileManager_Listbox.insert(tk.END, file.strip())

    def c_cd_u(self):
        self.to_stdout("cd ~")
        self.c_cd("~")

    def c_cd_up(self):
        self.to_stdout("cd ..")
        self.c_cd(self.pwd+"/..")


    def to_stdout(self, str):
        self.UI.Stdout_Text.insert(tk.END, str+"\n")
        self.UI.Stdout_Text.see(tk.END)

        
    def FM_double_click(self, event):
        name=self.UI.FileManager_Listbox.get(self.UI.FileManager_Listbox.curselection())
        if name in self.Current_Dirs:
            self.to_stdout("cd "+self.pwd+"/"+name)
            self.c_cd(self.pwd+"/"+name)
            
        elif name in self.Current_Files:
            
            Preview=tk.Toplevel()
            Preview.geometry("400x600")
            Preview.geometry(f"{500}x{600}+{100}+{100}")

            Preview_Text=tk.Text(Preview, font=("Consolas",11))
            Preview_Scl=tk.Scrollbar(Preview)

            Preview_Scl.config(command=Preview_Text.yview)
            Preview_Text.config(yscrollcommand=Preview_Scl)

            Preview_Scl.pack(side=tk.RIGHT, fill=tk.Y)
            Preview_Text.pack(side=tk.TOP, fill=tk.BOTH, expand=True)


            content=self.stdout_cmd(f"cat \"{self.pwd}/{name}\"")
            Preview_Text.insert(tk.END, content)

        
    def c_refresh(self):
        self.to_stdout("cd "+self.pwd)
        self.c_cd(self.pwd)

    def c_rename(self):
        if not self.Connected:
            return
        
        s=self.UI.FileManager_Listbox.curselection()
        if len(s)>1:
            messagebox.showinfo("重命名", "不支持批量重命名！")
            return
        for i in s:
            if not ( self.UI.FileManager_Listbox.get(i) != dir_sepa and self.UI.FileManager_Listbox.get(i) != file_sepa):
                messagebox.showerror("错误", "选择了分割线！")
                return
            file=self.UI.FileManager_Listbox.get(i)
            s=simpledialog.askstring("重命名", f"将{file}重命名为")
            if not s is None:
                self.to_stdout(f"mv \"{self.pwd}/{file}\" \"{self.pwd}/{s.strip()}\"")
                self.to_stdout(self.stdout_cmd(f"mv \"{self.pwd}/{file}\" \"{self.pwd}/{s.strip()}\""))
                self.c_refresh()
            else:
                messagebox.showinfo("重命名","未输入文件名，取消操作")
            return

    def c_mkdir(self):
        if not self.Connected:
            return
        
        s=simpledialog.askstring("新建文件夹", "文件夹名称", initialvalue="New Folder_"+str(random.randint(1,99)))
        if not s is None:
            self.to_stdout(f"mkdir \"{self.pwd}/{s.strip()}\"")
            self.to_stdout(self.stdout_cmd(f"mkdir \"{self.pwd}/{s.strip()}\""))
            self.c_refresh()

    def c_rm(self):
        if not self.Connected:
            return
        
        selection=self.UI.FileManager_Listbox.curselection()

        files=""
        for i in selection:
            files=files+"\n"+self.UI.FileManager_Listbox.get(i)
            if not (self.UI.FileManager_Listbox.get(i) != dir_sepa and self.UI.FileManager_Listbox.get(i) != file_sepa):
                messagebox.showerror("错误", "选择了分割线！")
                return
        if len(files.strip())==0:
            return
        if not messagebox.askokcancel("删除", f"确认删除以下文件？删除后无法恢复！{files}"):
            return

        for i in selection:
            file=self.UI.FileManager_Listbox.get(i)
            self.to_stdout(f"rm -rf \"{self.pwd}/{file}\"")
            self.to_stdout(self.stdout_cmd(f"rm -rf \"{self.pwd}/{file}\""))
        self.c_refresh()

    def c_mv(self):
        if not self.Connected:
            return
        selection=self.UI.FileManager_Listbox.curselection()
        files=""
        for i in selection:
            files=files+self.UI.FileManager_Listbox.get(i)+'\n'
            if not (self.UI.FileManager_Listbox.get(i) != dir_sepa and self.UI.FileManager_Listbox.get(i) != file_sepa):
                messagebox.showerror("错误", "选择了分割线！")
                return
        if len(files.strip())==0:
            return
        
        s=simpledialog.askstring("移动", f"{files}将以上文件移动到", initialvalue=self.pwd)

        if not s is None:
            isdir=self.stdout_cmd(f"[ -d \"{s}\" ] && echo 1").strip()
            if not isdir=="1":
                messagebox.showerror("移动", "目标路径非法！")
                return

            newpath=self.stdout_cmd(f"cd \"{s}\"; pwd")
            if newpath==self.pwd:
                messagebox.showerror("移动", "源文件夹与目标文件夹相同！")
            for i in selection:
                file=self.UI.FileManager_Listbox.get(i)
                self.to_stdout(f"mv \"{self.pwd}/{file}\" \"{newpath}/{file}\" -f")
                self.to_stdout(self.stdout_cmd(f"mv \"{self.pwd}/{file}\" \"{newpath}/{file}\" -f"))
        else:
            messagebox.showinfo("移动","未输入路径，取消操作！")

        self.c_refresh()
        return
    def c_cp(self):
        if not self.Connected:
            return
        selection=self.UI.FileManager_Listbox.curselection()
        files=""
        for i in selection:
            files=files+self.UI.FileManager_Listbox.get(i)+'\n'
            if not (self.UI.FileManager_Listbox.get(i) != dir_sepa and self.UI.FileManager_Listbox.get(i) != file_sepa):
                messagebox.showerror("错误", "选择了分割线！")
                return
        if len(files.strip())==0:
            return
        
        s=simpledialog.askstring("复制", f"{files}将以上文件复制到文件夹", initialvalue=self.pwd)

        if not s is None:
            s=s.strip()
            isdir=self.stdout_cmd(f"[ -d \"{s}\" ] && echo 1").strip()
            if not isdir=="1":
                messagebox.showerror("复制", "目标路径非法！")
            
            newpath=self.stdout_cmd(f"cd \"{s}\"; pwd")
            if newpath==self.pwd:
                if len(selection)!=1:
                    messagebox.showerror("复制", "源文件夹与目标文件夹相同，只能复制一个对象！")
                    return
                file=file=self.UI.FileManager_Listbox.get(selection[0])
                s=simpledialog.askstring("复制", f"{file}将以上文件命名为", initialvalue=file)
                self.to_stdout(f"cp \"{self.pwd}/{file}\" \"{newpath}/{s}\" -rf")
                self.to_stdout(self.stdout_cmd(f"cp \"{self.pwd}/{file}\" \"{newpath}/{s}\" -rf"))

            for i in selection:
                file=self.UI.FileManager_Listbox.get(i)
                self.to_stdout(f"cp \"{self.pwd}/{file}\" \"{newpath}/{file}\" -rf")
                self.to_stdout(self.stdout_cmd(f"cp \"{self.pwd}/{file}\" \"{newpath}/{file}\" -rf"))
        else:
            messagebox.showinfo("复制","未输入路径，取消操作！")

        self.c_refresh()
        return

    def f_upload(self):
        if not self.Connected:
            return
        # sftp=sshClient()
        # sftp.Connect(self.para["Server"], self.para["Port"], self.para["Username"], self.para["Password"])

        # sftp=paramiko.SFTPClient.from_transport(self.sshc_transport)
        
        file_paths=filedialog.askopenfilenames(title="选择文件")

        if not file_paths:
            return
        if len(file_paths)==1 and os.path.isfile:
            self.Status("Uploading...")
            self.to_stdout(f"Upload({file_paths[0]},{self.pwd}/{os.path.basename(file_paths[0])})")
            if not self.sshc.Upload(file_paths[0],self.pwd+"/"+os.path.basename(file_paths[0])):
                self.Status("Upload Failed")
                return
            self.c_refresh()
            messagebox.showinfo("上传文件", "上传完成！")
            return
        
        with tempfile.NamedTemporaryFile(suffix=".zip") as zfile:
            self.Status("Uploading...")
            os.remove(zfile.name)
            zip=zipfile.ZipFile(zfile.name, 'w', zipfile.ZIP_DEFLATED)
            for f in file_paths:
                self.to_stdout(f"Zip {os.path.basename(f)}")
                zip.write(f,os.path.basename(f))
            zip.close()
            self.to_stdout(f"Upload({zfile.name},{self.pwd}/{os.path.basename(zfile.name)})")
            if not self.sshc.Upload(zfile.name,self.pwd+"/"+os.path.basename(zfile.name)):
                self.Status("Upload Failed")
                return
            self.to_stdout(self.stdout_cmd(f"unzip -O CP936 {self.pwd}/{os.path.basename(zfile.name)} -d {self.pwd}; rm -f {self.pwd}/{os.path.basename(zfile.name)}"))
                
            self.Status("Done Upload")
            self.c_refresh()
            messagebox.showinfo("上传文件", "上传完成！")
            return
        
        messagebox.showerror("上传错误", "文件未上传")

    def f_upload_dir(self):
        if not self.Connected:
            return
        
        dir_path=filedialog.askdirectory(title="选择文件夹")

        if not dir_path:
            return

        with tempfile.NamedTemporaryFile(suffix=".zip") as zfile:
            self.Status("Uploading...")
            os.remove(zfile.name)
            zip=zipfile.ZipFile(zfile.name, 'w', zipfile.ZIP_DEFLATED)

            for path, dirnames, filenames in os.walk(dir_path):
                fpath=path.replace(dir_path, "")
                for filename in filenames:
                    self.to_stdout(f"Zip {os.path.basename(os.path.join(path, filename))}")
                    zip.write(os.path.join(path, filename), os.path.join(fpath, filename))
            zip.close()
            self.to_stdout(f"Upload({zfile.name},{self.pwd}/{os.path.basename(zfile.name)})")
            if not self.sshc.Upload(zfile.name,self.pwd+"/"+os.path.basename(zfile.name)):
                self.Status("Upload Failed")
                return
            self.to_stdout(self.stdout_cmd(f"mkdir {os.path.basename(dir_path)}; unzip -O CP936 {self.pwd}/{os.path.basename(zfile.name)} -d {self.pwd}/{os.path.basename(dir_path)}; rm -f {self.pwd}/{os.path.basename(zfile.name)}"))
            self.Status("Done Upload")
            self.c_refresh()
            messagebox.showinfo("上传文件", "上传完成！")
            return
        
        messagebox.showerror("上传错误", "文件夹未上传")


    def f_download(self):
        if not self.Connected:
            return
        
        # sftp=sshClient()
        # sftp.Connect(self.para["Server"], self.para["Port"], self.para["Username"], self.para["Password"])
        
        # sftp=paramiko.SFTPClient.from_transport(self.sshc_transport)
        # sftp=self.sshc.client.open_sftp()

        selection=self.UI.FileManager_Listbox.curselection()
        files=""
        for i in selection:
            files=files+"\n"+self.UI.FileManager_Listbox.get(i)
            if not (self.UI.FileManager_Listbox.get(i) != dir_sepa and self.UI.FileManager_Listbox.get(i) != file_sepa):
                messagebox.showerror("错误", "选择了分割线！")
                return
        if len(files.strip())==0:
            return
        if not messagebox.askokcancel("下载", f"下载以下文件？{files}"):
            return

        
        if len(selection)==1 and self.UI.FileManager_Listbox.get(selection[0]) in self.Current_Files:
            source=self.UI.FileManager_Listbox.get(selection[0])
            dest=filedialog.asksaveasfilename(
                title="保存文件名", 
                initialfile=source
            )
            self.Status("Downloading...")
            self.to_stdout(f"Download({self.pwd+'/'+source},{dest})")
            if not self.sshc.Download(self.pwd+"/"+source, dest):
                self.Status("Download Failed")
                return
            self.Status("Done Download")
            messagebox.showinfo("下载文件", "下载完成！")
            return
        
        dest=filedialog.asksaveasfilename(
            title="保存文件名", 
            initialfile=self.stdout_cmd(f"basename \"{self.pwd}\"")+".zip",
            filetypes=[("Zip File", "*.zip")]
        )

        self.Status("Downloading...")
        # self.stdout_cmd(r"if [ ! -d $HOME/.tmp ];then mkdir $HOME/.tmp; fi")
        # self.stdout_cmd(r"if [ ! -d $HOME/.tmp/Slurm_Submit ];then mkdir $HOME/.tmp/Slurm_Submit; fi")
        tempfile=self.stdout_cmd(r"mktemp XXXXXX.zip -t")
        print(tempfile)
        self.stdout_cmd(f"rm {tempfile}")
        for i in selection:
            source=self.UI.FileManager_Listbox.get(i)
            self.to_stdout(self.stdout_cmd(f"cd \"{self.pwd}\"; zip -r {tempfile} \"{source}\""))

        self.to_stdout(f"Download({tempfile},{dest})")
        if not self.sshc.Download(tempfile, dest):
            self.Status("Download Failed")
            return

        self.stdout_cmd(f"rm {tempfile}")
        self.Status("Done Download")
        messagebox.showinfo("下载文件", "下载完成！")

                   

        
        

    
    def Login(self, event=None):
        self.get_para()
        self.Status("Connecting Server")
        self.sshc.Connect(self.para["Server"], self.para["Port"], self.para["Username"], self.para["Password"])
        self.Status("Ready")
        if not self.sshc.Connected:
            return
        self.UI.serverstatusbar["text"]=f'已连接到服务器{self.para["Server"]}:{self.para["Port"]}'
        self.Connected=True
        self.c_cd("~")

        # self.channel.set
        self.TC_reconnect()
        thread_func(self.keep_terminal)

    def C_wd_selcur(self):
        if not self.Connected:
            return
        self.Entry_Text(self.UI.WorkingDir_Entry, self.pwd)
        self.get_para()

    
    def C_jo_selcur(self):
        if not self.Connected:
            return
        selection=self.UI.FileManager_Listbox.curselection()
        if not (len(selection)==1 and self.UI.FileManager_Listbox.get(selection[0]) in self.Current_Files):
            messagebox.showinfo("选择Journal", "选且仅选1个Journal文件")
        self.Entry_Text(self.UI.Journal_Entry, self.UI.FileManager_Listbox.get(selection[0]))
        self.get_para()
    
    def C_wd_tail(self):
        if not self.Connected:
            return
        self.get_para()
        self.channel.send(f'tail \"{self.para["WorkingDir"]}/Result_{self.para["Journal"]}/stdout_fluent.txt\" -f &'+"\n")

    

    def S_submit(self):
        if not self.Connected:
            return
        
        self.get_para()
        if self.para["Journal"][-4:] != ".jou":
            messagebox.showwarning("警告", "选择的Journal文件，不是*.jou")
            return
        self.stdout_cmd(f'dos2unix \"{self.para["WorkingDir"]}/{self.para["Journal"]}\"')

        args=[self.para["WorkingDir"], self.para["Version"],self.para["Solver"],self.para["Journal"],self.para["Partition"],self.para["Core"],self.para["Account"]]
        if not messagebox.askokcancel("提交作业", f"工作文件夹：{args[0]}\nFluent版本：{args[1]}\n求解器：{args[2]}\nJournal脚本：{args[3]}\n计算分区：{args[4]}\n核心数量：{args[5]}\n计费账户：{args[6]}\n确认提交？"):
            return
        sh=runfluentsh
        for i in range(0,7):
            sh=re.sub(r"\$"+f"{i+1}",args[i], sh)
        # messagebox.showinfo("脚本",sh)
        self.channel.send(sh)
        self.channel.send(f"cd {self.pwd}"+"\n")
        self.C_wd_tail()
        resdir=f'{self.pwd}/Result_{self.para["Journal"]}'.rsplit('.', 1)[0]
        self.to_stdout(f"cd {resdir}")
        self.c_cd(resdir)
    

    def S_scancel(self):
        if not self.Connected:
            return
        jobid=self.UI.Scancel_Entry.get().strip()
        if jobid=="":
            return
        if messagebox.askokcancel("取消作业", f"取消作业{jobid}？"):
            self.channel.send(f"scancel {jobid}"+"\n")
    
    def S_scancel_u(self):
        if not self.Connected:
            return
        if messagebox.askokcancel("取消作业", "取消用户全部作业？"):
            self.channel.send(r"scancel -u $USER"+"\n")
    
    def S_stoptail(self):
        if not self.Connected:
            return
        self.channel.send("\x03")
        self.channel.send(r"pkill tail"+"\n")
    
    def S_sinfo(self):
        if not self.Connected:
            return
        self.channel.send("sinfo"+"\n")

    def S_squeue(self):
        if not self.Connected:
            return
        self.channel.send("squeue -u $USER"+"\n")

    def S_sacct(self):
        if not self.Connected:
            return
        self.channel.send("sacct"+"\n")
    
    def I_sendcmd(self, event=None):
        if not self.Connected:
            return
        cmd=self.Command_Entry.get().strip()
        self.channel.send(cmd+"\n")
        self.Entry_Text(self.UI.Command_Entry,"")

    def I_cls(self):
        self.UI.Terminal_Text.delete('1.0',tk.END)
        
    def TC_reconnect(self):
        try:
            self.channel.close()
        except:
            pass
        self.channel=self.sshc.client.invoke_shell(width=self.UI.Terminal_Text.winfo_width()//8)
    def keep_terminal(self):
        rev=None
        while True:
            time.sleep(0.1)
            try:
                rev=self.channel.recv(4096)
                # print(rev)
                rev=re.sub(rb'\x1b(\[.*?[@-~]|\].*?(\x07|\x1b\\))', rb'', rev)
                # rev=rev.decode("utf-8", "ignore")
                if len(rev)==0:
                    continue
                self.UI.Terminal_Text.insert(tk.END,rev.decode("utf-8", "ignore"))
                self.UI.Terminal_Text.see("end")


            except Exception as e:
                print(e)
                pass


    def TC_expand_Bash(self):
        if self.ShowFS:
            self.UI.File_Frame.pack_forget()
            self.UI.Set_Frame.pack_forget()
            self.ShowFS=False
        else:
            self.UI.Bash_Frame.pack_forget()
            self.UI.File_Frame.pack(padx=(20,10), pady=20, side=tk.LEFT, anchor=tk.W, fill=tk.Y)
            self.UI.Set_Frame.pack(padx=10, pady=20, side=tk.LEFT, anchor=tk.W, fill=tk.Y)
            self.UI.Bash_Frame.pack(padx=(10,20), pady=20, side=tk.LEFT, anchor=tk.E, fill=tk.BOTH, expand=True)
            self.ShowFS=True
        
    def w_popout(self, event=None):
        # name=self.UI.FileManager_Listbox.get(self.UI.FileManager_Listbox.curselection())
        menu=tk.Menu(self.UI.FileManager_Listbox, tearoff=0)
        menu.add_cascade(label="复制", command=self.c_cp)
        menu.add_cascade(label="移动", command=self.c_mv)
        menu.add_cascade(label="删除", command=self.c_rm)
        menu.add_cascade(label="重命名", command=self.c_rename)
        menu.add_cascade(label="上传", command=self.f_upload)
        menu.add_cascade(label="下载", command=self.f_download)
        menu.add_cascade(label="新建文件夹", command=self.c_mkdir)

        menu.post(event.x+self.UI.root.winfo_rootx(), event.y+self.UI.root.winfo_rooty())

        

        

        
    
class Slurm_Submit():
    def __init__(self):
        self.init_cfg()
        
        self.UI=Application()


    def init_cfg(self):
        home_path=os.path.expanduser('~')
        cfg_path=home_path+'/.config'
        if os.path.isfile(cfg_path):
            messagebox.showerror("错误", f"无法在 {home_path} 下创建 .config 文件夹。\n存在同名文件！")
            exit(1)
        cfg_path=cfg_path+'/Slurm_Submit'
        if not os.path.isdir(cfg_path):
            os.makedirs(cfg_path)
        cfg_path=cfg_path+'/default.json'
        if not os.path.isfile(cfg_path):
            self.write_cfg(cfg_path)

    def write_cfg(self, cfg_path):
        data={
            "Server": "",
            "Port": "",
            "Username": "",
            "Password": "",
            "Version": "",
            "Solver": "",
            "Partition": "",
            "Core": "",
            "Account": "",
            "WorkingDir": "",
            "Journal": ""
        }
        with open(cfg_path, "w") as cfg:
            json.dump(data, cfg, indent=4)
        


runfluentsh=r"""
FLUENT_SOLVER_VER=$3
JOU_FILE=$4 
SLURM_PARTITION=$5 
SLURM_NTASKS=$6 
SLURM_ACCOUNT=$7 
module load app/fluent/$2 
cd "$1"
SLURM_JOB_NAME=$JOU_FILE 
dos2unix $JOU_FILE 
if [ ! -d $HOME/.fluent_resdir ];then
    mkdir $HOME/.fluent_resdir
fi
TEMP_D=$(mktemp -d -p $HOME/.fluent_resdir) || exit 1
SOURCE_D=$PWD
RESULT_DNAME="Result_`basename $JOU_FILE .jou`"
if [ -e $RESULT_DNAME ] || [ -L $RESULT_DNAME ]; then
    LAST_RESULT_D="LastRun$RESULT_DNAME"
    if [ -e $LAST_RESULT_D ] || [ -L $LAST_RESULT_D ]; then
        rm -rf $(readlink -f $LAST_RESULT_D)
    fi
    mv -f $RESULT_DNAME "LastRun$RESULT_DNAME"
fi
ln -s $TEMP_D $RESULT_DNAME

cd "$TEMP_D"
for f in $(ls $SOURCE_D)
do
    if [ ! -L $SOURCE_D/$f ] && [ $f != $RESULT_DNAME ] ;then
        ln -s $SOURCE_D/$f
    fi
done
echo "" > stdout_fluent.txt
echo "" > stderr_fluent.txt
fluent $FLUENT_SOLVER_VER -g \
       -t$SLURM_NTASKS \
       -i  $JOU_FILE\
       -mpi=intel -pib -scheduler=slurm \
       -scheduler_queue=$SLURM_PARTITION \
       -scheduler_opt="--comment=$SLURM_ACCOUNT" \
       -scheduler_stdout=stdout_fluent.txt \
       -scheduler_stderr=stderr_fluent.txt \
       -scheduler_opt="--job-name=$SLURM_JOB_NAME"

"""

if __name__== '__main__':
    Slurm_Submit()

# To be implemented
# 拖拽上传文件
