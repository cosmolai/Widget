#!/usr/bin/python3
# -*- coding: UTF-8 -*-
#
# Tool to generate IPFW package template.
# Date: Dec 16, 2021
#
# Version 0.1: Initial version.


import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import yaml
from yaml.loader import SafeLoader
import os
import time

class App(tk.Frame):
    def __init__(self, tk, master):
        self.tk = tk
        self.master = master
        self.master.title('IPFW Package Generation Wizard')
        #self.master.geometry('800x400')
        row_index = 0
        # IPFW ipname
        self.ipfw_name_var = tk.StringVar()
        ipfw_name_lbl_title = tk.Label(master=self.master,text='IP NAME:')
        ipfw_name_lbl_title.grid(row=row_index, column=0, sticky='E', padx = 12, pady=20)
        ipfw_name_entry = tk.Entry(master=self.master, textvariable=self.ipfw_name_var)
        ipfw_name_entry.grid(row=row_index, column=1, sticky='W')
        row_index+=1
        # IPFW path
        self.ipfw_path_var = tk.StringVar()
        ipfw_path_lbl_title = tk.Label(master=self.master,text='IPFW PATH:', padx = 12)
        ipfw_path_lbl_title.grid(row=row_index, column=0, sticky='E')
        ipfw_path_entry = tk.Entry(master=self.master, textvariable=self.ipfw_path_var, width=40)
        ipfw_path_entry.grid(row=row_index, column=1, sticky='W')
        ipfw_path_button = tk.Button(text="Browse", command=self.button_ipfw_folder)
        ipfw_path_button.grid(row=row_index, column=2, padx = 10)
        row_index+=1
        # INTEL path
        self.intel_path_var = tk.StringVar()
        intel_path_lbl_title = tk.Label(master=self.master,text='INTEL PATH:', padx = 12)
        intel_path_lbl_title.grid(row=row_index, column=0, sticky='E')
        intel_path_entry = tk.Entry(master=self.master, textvariable=self.intel_path_var, width=40)
        intel_path_entry.grid(row=row_index, column=1, sticky='W')
        intel_path_button = tk.Button(text="Browse", command=self.button_intel_folder)
        intel_path_button.grid(row=row_index, column=2, padx = 10)
        row_index+=1
        # Create & Cancel
        ipfw_create_button = tk.Button(text="Create", command=self.button_create, fg='green')
        ipfw_create_button.grid(row=row_index, column=0, columnspan=2, pady=10)
        ipfw_cancel_button = tk.Button(text="Cancel", command=self.button_cancel, fg='red')
        ipfw_cancel_button.grid(row=row_index, column=1, columnspan=2)
        row_index+=1

    def button_ipfw_folder(self):
        filepath = filedialog.askdirectory()
        self.ipfw_path_var.set(filepath)
        print(self.ipfw_path_var.get())
        self.master.update()

    def button_intel_folder(self):
        filepath = filedialog.askdirectory()
        self.intel_path_var.set(filepath)
        print(self.intel_path_var.get())
        self.master.update()

    def button_create(self):
        print('Create...')
        print(self.ipfw_name_var.get())
        print(self.ipfw_path_var.get())
        print(self.intel_path_var.get())
        valid_input=True
        if len(self.ipfw_name_var.get()) == 0:
            print('Invalid IPFW name input: <empty>')
            valid_input=False
        if len(self.ipfw_path_var.get()) == 0:
            print('Invalid IPFW path input: <empty>')
            valid_input=False
        if len(self.intel_path_var.get()) == 0:
            print('Invalid INTEL path input: <empty>')
            valid_input=False
        if valid_input:
            self.generate_ipfwpkg(self.ipfw_name_var.get(), self.ipfw_path_var.get(), self.intel_path_var.get())
            messagebox.showinfo("Create IPFW package", "Complete... See console output for more information.")

    def button_cancel(self):
        print('Cancel...')
        self.master.destroy()

    def replace_one_keyword(self, filepath, filename, filecontent, keyword, replace_str):
        filepath = filepath.replace(keyword, replace_str)
        filename = filename.replace(keyword, replace_str)
        filecontent = filecontent.replace(keyword, replace_str)
        return filepath, filename, filecontent

    def replace_all_keyword(self, filepath, filename, filecontent, ipfwname, intelpath):
        # generate keyword replacement
        if not ipfwname.startswith('Ip'):
            ipfwname = 'Ip' + ipfwname
        ipfwnameuppercase = 'IP_' + ipfwname[2:].upper()
        copyright_year = int(time.strftime('%Y'))
        # replace keyword
        filepath, filename, filecontent = self.replace_one_keyword(filepath, filename, filecontent, '__IPNAME__', ipfwname)
        filepath, filename, filecontent = self.replace_one_keyword(filepath, filename, filecontent, '__IPNAMEUPPERCASE__', ipfwnameuppercase)
        filepath, filename, filecontent = self.replace_one_keyword(filepath, filename, filecontent, '__COPYRIGHT_YEAR__', str(copyright_year))
        filepath, filename, filecontent = self.replace_one_keyword(filepath, filename, filecontent, '__INTEL_PATH__', intelpath)
        return filepath, filename, filecontent

    def generate_ipfwpkg(self, ipfwname, ipfwpath, intelpath):
        with open('ipfwpkg_wizard.yaml') as f:
            yaml_file = yaml.load_all(f, Loader=SafeLoader)
            for yaml_doc in yaml_file:
                print('YAML file version: ' + yaml_doc['version'])
                for file in yaml_doc['filelist']:
                    filepath = file['path']
                    filename = file['name']
                    filecontent = file['content']
                    filepath, filename, filecontent = self.replace_all_keyword(filepath, filename, filecontent, ipfwname, intelpath)
                    #print(filepath)
                    #print(filename)
                    #print(filecontent)
                    fullpath = os.path.join(ipfwpath, filepath)
                    if not os.path.exists(fullpath):
                        os.mkdir(fullpath)
                    fullpathfile = fullpath + '/' + filename
                    if os.path.isfile(fullpathfile):
                        print('Skip file generation. File existed: ' + fullpathfile)
                        continue
                    with open(fullpathfile, 'w') as outputfile:
                        outputfile.write(filecontent)
                        print('Output: ' + fullpathfile)


root = tk.Tk()
myapp = App(tk,root)
tk.mainloop()
