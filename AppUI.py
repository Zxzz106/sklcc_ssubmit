import tkinter as tk
from tkinter import ttk
import os
from sshClient import sshClient
from thread_func import thread_func



class UI(object):
    def __init__(self, window, App):
        self.root=window
        self.App=App
        win_w,win_h=(1280,720)
        # win_w,win_h=(1366,768)
        # window.option_add("*Font", ("Times New Roman", 10))

        screen_w, screen_h=window.maxsize()
        x=int((screen_w-win_w)/2)
        y=int((screen_h-win_h)/2)
        window.title("Slurm作业提交器")
        window.geometry(f"{win_w}x{win_h}+{x}+{y}")
        # window.iconphoto(False,tk.PhotoImage(file='Hust_HPC.png')

        menu=tk.Menu(window)
        window.config(menu=menu)

        # M_Files=tk.Menu(menu, tearoff=0)
        # M_Files.add_command(label="打开配置文件", command=self.open_cfg)
        # M_Files.add_command(label="保存配置文件", command=self.save_cfg)
        # menu.add_cascade(label="文件", menu=M_Files)
        
        menu.add_command(label="打开配置文件", command=App.open_cfg)
        menu.add_command(label="保存配置文件", command=App.save_cfg)

        statusbar_Frame=tk.Frame(window, bd=1, relief=tk.SUNKEN)
        statusbar_Frame.pack(side=tk.BOTTOM, fill=tk.X)
        self.statusbar=tk.Label(statusbar_Frame, text="Starting...")
        self.statusbar.pack(side=tk.LEFT, anchor=tk.W)
        self.serverstatusbar=tk.Label(statusbar_Frame, text="未连接服务器")
        self.serverstatusbar.pack(side=tk.RIGHT)

        self.def_FileFrame()
        self.def_SetFrame()
        self.def_BashFrame()
           
        # self.sshc_transport=self.sshc.client.get_transport()

        
        
    

    def def_FileFrame(self):
        self.File_Frame=tk.Frame(self.root)
        self.File_Frame.pack(padx=(20,10), pady=20, side=tk.LEFT, anchor=tk.W, fill=tk.Y)

        Login_Frame=tk.Frame(self.File_Frame, relief=tk.SUNKEN, bd=1)
        Login_Frame.pack(side=tk.TOP)

        
        LoginLabel_Frame=tk.Frame(Login_Frame)
        LoginEntry_Frame=tk.Frame(Login_Frame)
        LoginButton=tk.Button(Login_Frame, text="登录", width=10, height=3, command=lambda :thread_func(self.App.Login))
        LoginLabel_Frame.pack(side=tk.LEFT, padx=5)
        LoginEntry_Frame.pack(side=tk.LEFT, padx=5)
        LoginButton.pack(side=tk.LEFT, padx=5)


        Server_Label=tk.Label(LoginLabel_Frame, text="服务器")
        Username_Label=tk.Label(LoginLabel_Frame, text="用户名")
        Password_Label=tk.Label(LoginLabel_Frame, text="密码")
        Server_Label.pack(side=tk.TOP, pady=5, anchor=tk.E)
        Username_Label.pack(side=tk.TOP, pady=5, anchor=tk.E)
        Password_Label.pack(side=tk.TOP, pady=5, anchor=tk.E)

        ServerEntry_Frame=tk.Frame(LoginEntry_Frame)
        self.Server_Entry=tk.Entry(ServerEntry_Frame, width=14)
        ServerColon_Label=tk.Label(ServerEntry_Frame, text=":")
        self.ServerPort_Entry=tk.Entry(ServerEntry_Frame, width=5)
        self.Username_Entry=tk.Entry(LoginEntry_Frame, width=21)
        self.Password_Entry=tk.Entry(LoginEntry_Frame, show="·", width=21)
        ServerEntry_Frame.pack(side=tk.TOP, pady=5)
        self.Server_Entry.pack(side=tk.LEFT)
        ServerColon_Label.pack(side=tk.LEFT)
        self.ServerPort_Entry.pack(side=tk.RIGHT, padx=(2,0))
        self.Username_Entry.pack(side=tk.TOP, pady=5)
        self.Password_Entry.pack(side=tk.TOP, pady=5)
        self.Password_Entry.bind("<Return>", self.App.Login)

        FileManager_Frame=tk.Frame(self.File_Frame)
        FileManager_Frame.pack(pady=(5,0), side=tk.TOP, expand=True, fill=tk.BOTH)






        FileButton_Frame1=tk.Frame(FileManager_Frame)
        

        CurrentDir_Frame=tk.Label(FileManager_Frame)
        CurrentDir_Frame.pack(side=tk.TOP, fill=tk.X)

        CurrentDir_Label=tk.Label(CurrentDir_Frame, text="当前目录：")
        CurrentDir_Label.pack(side=tk.LEFT, pady=(5,0))
        self.CurrentDir_Path=tk.Entry(CurrentDir_Frame)
        self.CurrentDir_Path.pack(side=tk.LEFT, expand=True, fill=tk.X, anchor=tk.W, padx=(5,0))

        File_Up_Button=tk.Button(FileButton_Frame1, text="新建文件夹", command=self.App.c_mkdir)
        File_Up_Button.pack(side=tk.LEFT, padx=(0,5))
        File_Up_Button=tk.Button(FileButton_Frame1, text="用户目录", command=self.App.c_cd_u)
        File_Up_Button.pack(side=tk.LEFT, padx=(5,5))
        File_Up_Button=tk.Button(FileButton_Frame1, text="上级目录", command=self.App.c_cd_up)
        File_Up_Button.pack(side=tk.LEFT, padx=(5,5))
        File_Up_Button=tk.Button(FileButton_Frame1, text="刷新", command=self.App.c_refresh)
        File_Up_Button.pack(side=tk.LEFT, padx=(5,0))

        self.FileManager_Listbox=tk.Listbox(FileManager_Frame, selectmode=tk.EXTENDED)
        # FileManager_yScrollbar=tk.Scrollbar(FileManager_Frame, width=2)
        # FileManager_yScrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.FileManager_Listbox.config()
        self.FileManager_Listbox.pack(side=tk.TOP,expand=True, fill=tk.BOTH, pady=(0,0))

        self.FileManager_Listbox.bind("<Double-Button-1>", self.App.FM_double_click)
        self.FileManager_Listbox.bind("<Button-3>", self.App.w_popout)
        

        FileButton_Frame2=tk.Frame(FileManager_Frame)
        FileButton_Frame2.pack(side=tk.BOTTOM, pady=(5,0))
        FileButton_Frame1.pack(side=tk.BOTTOM, pady=(5,0))
        
        File_Del_Button=tk.Button(FileButton_Frame2, text="复制", command=self.App.c_cp)
        File_Del_Button.pack(side=tk.LEFT, padx=(0,5))
        File_Del_Button=tk.Button(FileButton_Frame2, text="移动", command=self.App.c_mv)
        File_Del_Button.pack(side=tk.LEFT, padx=(5,5))
        File_Del_Button=tk.Button(FileButton_Frame2, text="删除", command=self.App.c_rm)
        File_Del_Button.pack(side=tk.LEFT, padx=(5,5))
        # File_Del_Button=tk.Button(FileButton_Frame2, text="重命名", command=self.App.c_rename)
        # File_Del_Button.pack(side=tk.LEFT, padx=(5,5))
        File_Upload_Button=tk.Button(FileButton_Frame2, text="上传", command=lambda :thread_func(self.App.f_upload))
        File_Upload_Button.pack(side=tk.LEFT, padx=(5,5))
        File_Upload_Button=tk.Button(FileButton_Frame2, text="上传文件夹", command=lambda :thread_func(self.App.f_upload_dir))
        File_Upload_Button.pack(side=tk.LEFT, padx=(5,5))
        File_Upload_Button=tk.Button(FileButton_Frame2, text="下载", command=lambda :thread_func(self.App.f_download))
        File_Upload_Button.pack(side=tk.LEFT, padx=(5,0))

    def def_SetFrame(self):
        self.Set_Frame=tk.Frame(self.root)
        self.Set_Frame.pack(padx=10, pady=20, side=tk.LEFT, anchor=tk.W, fill=tk.Y)

        VS_Frame=tk.Frame(self.Set_Frame)
        VS_Frame.pack(side=tk.TOP, anchor=tk.W)
        Ver_Label=tk.Label(VS_Frame, text="版本")
        Ver_Label.pack(side=tk.LEFT, padx=(0,5))
        self.Ver_Combobox=ttk.Combobox(VS_Frame, values=("17.2","19.2","20.2.0","22.1","23.1"), width=5)
        self.Ver_Combobox.pack(side=tk.LEFT)
        Solver_Label=tk.Label(VS_Frame, text="求解器")
        Solver_Label.pack(side=tk.LEFT, padx=(10,5))
        self.Solver_Combobox=ttk.Combobox(VS_Frame, values=("2d","2ddp","3d","3ddp"), width=5)
        self.Solver_Combobox.pack(side=tk.LEFT)


        WorkingDirLB_Frame=tk.Frame(self.Set_Frame)
        WorkingDirLB_Frame.pack(side=tk.TOP, fill=tk.X, pady=(10,0))
        WorkingDir_Label=tk.Label(WorkingDirLB_Frame, text="工作文件夹")
        WorkingDir_Label.pack(side=tk.LEFT, anchor=tk.W, padx=(0,5))
        WorkingDirS_Button=tk.Button(WorkingDirLB_Frame, text="选择当前", command=self.App.C_wd_selcur)
        WorkingDirS_Button.pack(side=tk.LEFT, padx=(0,5))
        WorkingDirT_Button=tk.Button(WorkingDirLB_Frame, text="跟踪输出", command=lambda: thread_func(self.App.C_wd_tail))
        WorkingDirT_Button.pack(side=tk.LEFT, padx=(0,5))
        WorkingDir_Frame=tk.Frame(self.Set_Frame)
        WorkingDir_Frame.pack(side=tk.TOP, fill=tk.X, pady=(5,0))
        self.WorkingDir_Entry=tk.Entry(WorkingDir_Frame)
        self.WorkingDir_Entry.pack(side=tk.BOTTOM, anchor=tk.W, fill=tk.X)

        JournalLB_Frame=tk.Frame(self.Set_Frame)
        JournalLB_Frame.pack(side=tk.TOP, fill=tk.X, pady=(10,0))
        Journal_Label=tk.Label(JournalLB_Frame, text="Journal文件")
        Journal_Label.pack(side=tk.LEFT, anchor=tk.W, padx=(0,5))
        Journal_Button=tk.Button(JournalLB_Frame, text="选择", command=self.App.C_jo_selcur)
        Journal_Button.pack(side=tk.LEFT)
        Journal_Frame=tk.Frame(self.Set_Frame)
        Journal_Frame.pack(side=tk.TOP, fill=tk.X, pady=(5,0))
        self.Journal_Entry=tk.Entry(Journal_Frame)
        self.Journal_Entry.pack(side=tk.BOTTOM, anchor=tk.W, fill=tk.X)

        PP_Frame=tk.Frame(self.Set_Frame)
        PP_Frame.pack(side=tk.TOP, anchor=tk.W, pady=(10,0))
        Partition_Label=tk.Label(PP_Frame, text="分区")
        Partition_Label.pack(side=tk.LEFT, padx=(0,5))
        self.Partition_Entry=tk.Entry(PP_Frame)
        self.Partition_Entry.pack(side=tk.LEFT, fill=tk.X)
        Processor_Label=tk.Label(PP_Frame, text="核心")
        Processor_Label.pack(side=tk.LEFT, padx=(10,5))
        self.Processor_Spinbox=tk.Spinbox(PP_Frame, width=5, from_=1, to=999)
        self.Processor_Spinbox.pack(side=tk.LEFT)

        Account_Frame=tk.Frame(self.Set_Frame)
        Account_Frame.pack(side=tk.TOP, anchor=tk.W, pady=(10,0), fill=tk.X)
        Account_Label=tk.Label(Account_Frame, text="计费账户")
        Account_Label.pack(side=tk.LEFT, padx=(0,5))
        self.Account_Entry=tk.Entry(Account_Frame)
        self.Account_Entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        Job_Frame=tk.Frame(self.Set_Frame)
        Job_Frame.pack(side=tk.TOP, pady=(20,0))
        Submit_Button=tk.Button(Job_Frame, text="提交作业", command=self.App.S_submit)
        Submit_Button.pack(side=tk.TOP)
        Scancel_Frame=tk.Frame(Job_Frame)
        Scancel_Frame.pack(side=tk.TOP, pady=(20,0))
        Scancel_Button=tk.Button(Scancel_Frame, text="中止用户全部作业", command=self.App.S_scancel_u)
        Scancel_Button.pack(side=tk.TOP, pady=(0,20))
        Scancel_Button=tk.Button(Scancel_Frame, text="中止作业", command=self.App.S_scancel)
        Scancel_Button.pack(side=tk.LEFT)
        Scancel_Label=tk.Label(Scancel_Frame, text="Slurm作业ID")
        Scancel_Label.pack(side=tk.LEFT,padx=(10,0))
        self.Scancel_Entry=tk.Entry(Scancel_Frame, width=8)
        self.Scancel_Entry.pack(side=tk.LEFT,padx=(5,0))

        Stdout_Frame=tk.Frame(self.Set_Frame)
        Stdout_Frame.pack(side=tk.TOP, pady=(10,0), fill=tk.BOTH, expand=True)
        StdoutS_Buttoon=tk.Button(Stdout_Frame, text="清除", command=lambda :self.Stdout_Text.delete('1.0',tk.END))
        StdoutS_Buttoon.pack(side=tk.TOP, anchor=tk.E, pady=(0,5))
        Stdout_Scl=tk.Scrollbar(Stdout_Frame)
        self.Stdout_Text=tk.Text(Stdout_Frame, font=("Consolas",10), width=10, height=5, wrap="none")
        Stdout_Scl.pack(side=tk.RIGHT, fill=tk.Y)
        self.Stdout_Text.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.Stdout_Text.config(yscrollcommand=Stdout_Scl.set)
        Stdout_Scl.config(command=self.Stdout_Text.yview)

        Check_Frame=tk.Frame(self.Set_Frame)
        Check_Frame.pack(side=tk.BOTTOM)

        Slurm_Frame=tk.Frame(Check_Frame)
        Slurm_Frame.pack(side=tk.TOP, pady=(10,0))

        StopTail_Button=tk.Button(Slurm_Frame, text="停止输出", command=self.App.S_stoptail)
        StopTail_Button.pack(side=tk.LEFT)

        Sinfo_Button=tk.Button(Slurm_Frame, text="节点状态", command=self.App.S_sinfo)
        Sinfo_Button.pack(side=tk.LEFT, padx=(10,5))
        Squeue_Button=tk.Button(Slurm_Frame, text="作业队列", command=self.App.S_squeue)
        Squeue_Button.pack(side=tk.LEFT, padx=(5,10))
        Ssacct_Button=tk.Button(Slurm_Frame, text="历史作业", command=self.App.S_sacct)
        Ssacct_Button.pack(side=tk.LEFT)

        # Tail_Frame=tk.Frame(Check_Frame)
        # Tail_Frame.pack(side=tk.BOTTOM,pady=(20,0))
        # StopTail_Button=tk.Button(Tail_Frame, text="停止输出")
        # StopTail_Button.pack(side=tk.LEFT, padx=(0,20))
        # ContTail_Button=tk.Button(Tail_Frame, text="继续输出")
        # ContTail_Button.pack(side=tk.LEFT)
        
    def def_BashFrame(self):
        self.Bash_Frame=tk.Frame(self.root)
        self.Bash_Frame.pack(padx=(10,20), pady=20, side=tk.LEFT, anchor=tk.E, fill=tk.BOTH, expand=True)

        TerCtl_Frame=tk.Frame(self.Bash_Frame)
        TerCtl_Frame.pack(side=tk.TOP, fill=tk.X)
        
        TerExpand_Button=tk.Button(TerCtl_Frame, text="扩展终端", command=self.App.TC_expand_Bash)
        TerExpand_Button.pack(side=tk.RIGHT)
        Reconnect_Button=tk.Button(TerCtl_Frame, text="重连终端", command=self.App.TC_reconnect)
        Reconnect_Button.pack(side=tk.RIGHT, padx=(0,10))
        Cls_Button=tk.Button(TerCtl_Frame, text="清屏", command=self.App.I_cls)
        Cls_Button.pack(side=tk.RIGHT, padx=(0,10))

        TerCtl_Frame=tk.Frame(self.Bash_Frame)
        TerCtl_Frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, pady=(5,0))

        self.Terminal_Text=tk.Text(TerCtl_Frame, font=("Consolas",11), wrap="none")
        TerScl=tk.Scrollbar(TerCtl_Frame)
        TerScl.pack(side=tk.RIGHT, fill=tk.Y)
        self.Terminal_Text.pack(expand=True, fill=tk.BOTH)

        self.Terminal_Text.config(yscrollcommand=TerScl.set)
        TerScl.config(command=self.Terminal_Text.yview)

        # self.Terminal_Text.bind("<Key>", lambda a: "break")

        Command_Frame=tk.Frame(self.Bash_Frame)
        Command_Frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(10,0))
        
        Command_Button=tk.Button(Command_Frame, text="发送", command=self.App.I_sendcmd)
        Command_Button.pack(side=tk.RIGHT, padx=(10,0))
        self.Command_Entry=tk.Entry(Command_Frame, font=("Consolas",11))
        self.Command_Entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.Command_Entry.bind("<Return>", self.App.I_sendcmd)