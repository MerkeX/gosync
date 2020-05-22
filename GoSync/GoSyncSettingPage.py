import wx, subprocess, sys
#import wx.lib.agw.customtreectrl as CT
#from pydrive.drive import GoogleDrive
#from pydrive.auth import GoogleAuth
try :
    from .GoSyncEvents import *
except (ImportError, ValueError):
    from GoSyncEvents import *

use_system_notifs = True

sync_help = "GoSync monitors the local mirror directory for any changes like Add, Move, Delete. These changes are immediately reflected your Google Drive. But the sync from the Google Drive is done on a periodic basis. Below you can change the interval at which the remote Drive is sync'ed locally. More aggressive adds more network traffic."

class SettingsPage(wx.Panel):
    def __init__(self, parent, sync_model):
        wx.Panel.__init__(self, parent, style=wx.RAISED_BORDER)

        headerFont = wx.Font(11.5, wx.SWISS, wx.NORMAL, wx.FONTWEIGHT_NORMAL)

        self.sync_model = sync_model

        self.cb = wx.CheckBox(self, -1, 'Start sync at launch')
        self.notif_cb = wx.CheckBox(self, -1, 'Use system notifications for updates')
        self.cb.SetValue(True)
        self.notif_cb.SetValue(True)
        self.cb.Bind(wx.EVT_CHECKBOX, self.AutoSyncSetting)
        self.notif_cb.Bind(wx.EVT_CHECKBOX, self.OnUseSystemNotif)

        self.md = wx.StaticText(self, -1, self.sync_model.GetLocalMirrorDirectory(), pos=(0,0))
        self.md.SetFont(headerFont)
        self.si_spin_text = wx.StaticText(self, -1, "Sync Interval (in seconds): ")

        self.md_button = wx.Button(self, -1, "Change")
        self.show_button = wx.Button(self, -1, "Open Mirror Directory")
        self.show_button.Bind(wx.EVT_BUTTON, self.OnOpenMirror)
        self.md_button.Bind(wx.EVT_BUTTON, self.OnChangeMirror)

        self.si_spin_btn = wx.SpinCtrl(self, -1, min=30, max=86400)
        self.si_spin_btn.SetValue(self.sync_model.GetSyncInterval())
        self.Bind(wx.EVT_SPINCTRL, self.OnSyncIntervalSelect)
        if sys.version_info > (3,):
            ssizer = wx.StaticBoxSizer(wx.VERTICAL, self, "Local Mirror Directory")
            osizer = wx.StaticBoxSizer(wx.VERTICAL, self, "Other Settings")
        else:
            b = wx.StaticBox(self, -1, "Local Mirror Directory")
            ssizer = wx.StaticBoxSizer(b, wx.VERTICAL)
            c = wx.StaticBox(self, -1, "Other Settings")
            osizer = wx.StaticBoxSizer(c, wx.VERTICAL)

        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        si_spin_sizer = wx.BoxSizer(wx.HORIZONTAL)

        si_spin_sizer.Add(self.si_spin_text, 0, wx.ALL, 1)
        si_spin_sizer.Add(self.si_spin_btn, 1, wx.ALL)

        button_sizer.Add(self.md_button, 1, wx.ALL|wx.ALIGN_CENTER, border=5)
        button_sizer.Add(self.show_button, 2, wx.ALL|wx.ALIGN_CENTER)

        ssizer.Add(self.md, 0, wx.ALL, border=10)
        ssizer.AddSpacer(10)
        ssizer.Add(button_sizer, 1, wx.ALL|wx.ALIGN_CENTER)

        osizer.Add(self.cb, 0, wx.ALL, 0)
        osizer.Add(self.notif_cb, 1, wx.ALL, 0)
        osizer.Add(si_spin_sizer, 2, wx.ALL, 0)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.AddSpacer(10)
        sizer.Add(ssizer, 0, wx.EXPAND|wx.ALL)
        sizer.AddSpacer(20)
        sizer.Add(osizer, 1, wx.ALL|wx.EXPAND)
        sizer.AddSpacer(5)
        self.SetSizerAndFit(sizer)
        self.cb.SetValue(self.sync_model.GetAutoSyncState())
        self.notif_cb.SetValue(self.sync_model.GetUseSystemNotifSetting())

    def AutoSyncSetting(self, event):
        if self.cb.GetValue():
            self.sync_model.EnableAutoSync()
        else:
            self.sync_model.DisableAutoSync()

    def OnUseSystemNotif(self, event):
        if self.notif_cb.GetValue():
            self.sync_model.SetUseSystemNotifSetting(True)
        else:
            self.sync_model.SetUseSystemNotifSetting(False)

    def OnSyncIntervalSelect(self, event):
         interval = event.GetInt()
         self.sync_model.SetSyncInterval(interval)

    def OnOpenMirror(self, event):
        subprocess.check_call(['xdg-open', self.sync_model.GetLocalMirrorDirectory()])

    def OnChangeMirror(self, event):
        new_dir_help = "Your new local mirror directory is set. This will take effect after GoSync restart.\n\nPlease note that GoSync hasn't moved your files from old location. You would need to copy or move your current directory to new location before restarting GoSync."

        dlg = wx.DirDialog(None, "Choose target directory", "",
                           wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST)

        if dlg.ShowModal() == wx.ID_OK:
            self.sync_model.SetLocalMirrorDirectory(dlg.GetPath())
            resp = wx.MessageBox(new_dir_help, "IMPORTANT INFORMATION", (wx.OK | wx.ICON_WARNING))
            

        dlg.Destroy()
