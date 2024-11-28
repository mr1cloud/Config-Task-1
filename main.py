import os, tarfile, csv, argparse, posixpath, io
import tkinter as tk
from tkinter import messagebox
from datetime import datetime


class ShellEmulator:
    def __init__(self, hostname, vfs_path, log_path):
        self.hostname = hostname
        self.log_path = log_path
        self.vfs_path = vfs_path
        self.current_path = "/"
        self.fs = {}
        self.load_vfs(self.vfs_path)
        self.init_log()

    def load_vfs(self, vfs_path):
        """Загрузка файловой системы из tar-архива."""
        try:
            with tarfile.open(vfs_path, 'r') as tar:
                for member in tar.getmembers():
                    path_parts = member.name.strip("/").split("/")
                    current_level = self.fs
                    for part in path_parts[:-1]:
                        current_level = current_level.setdefault(part, {})
                    if member.isdir():
                        current_level[path_parts[-1]] = {}
                    else:
                        current_level[path_parts[-1]] = None
        except Exception as error:
            raise RuntimeError(f"Error loading VFS: {error}")

    def cp_in_tar(self, src, dest):
        """Копирование файла в tar-архиве."""
        file_data: bytes = None
        with tarfile.open(self.vfs_path, "r") as tar:
            file_data = tar.extractfile(src[1:]).read()

        with tarfile.open(self.vfs_path, "a") as tar:
            new_file_info = tarfile.TarInfo(name=dest[1:])
            new_file_info.size = len(file_data)
            tar.addfile(new_file_info, fileobj=io.BytesIO(file_data))

    def init_log(self):
        """Инициализация лог-файла."""
        with open(self.log_path, 'w', newline='') as log_file:
            writer = csv.writer(log_file)
            writer.writerow(["Timestamp", "Command", "Details"])

    def log_action(self, command, details=""):
        """Запись действия в лог."""
        with open(self.log_path, 'a', newline='') as log_file:
            writer = csv.writer(log_file)
            writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), command, details])

    def ls(self, path=None):
        """Вывод содержимого текущей директории."""
        current_dir = None
        if path is None:
            current_dir = self.navigate_to_path(self.current_path)
        else:
            current_dir = self.navigate_to_path(posixpath.join(self.current_path, path))
        print(f"Current directory: {current_dir}")
        if current_dir is None:
            return f"Error: '{self.current_path}' not found"
        return "\n".join(current_dir.keys())

    def cd(self, path):
        """Переход в другую директорию."""
        new_path = posixpath.normpath(posixpath.join(self.current_path, path)) if not path.startswith("/") else path
        print(f"Normalized path: {new_path}")
        target_dir = self.navigate_to_path(new_path)
        print(f"Target directory: {target_dir}")
        if target_dir is not None and isinstance(target_dir, dict):
            self.current_path = new_path
            self.current_dir = target_dir
            return "Changed directory to " + new_path
        else:
            return f"Error: '{new_path}' not found"

    def cp(self, src, dest):
        """Копирование файла или директории."""
        src_path = posixpath.normpath(posixpath.join(self.current_path, src)) if not src.startswith("/") else src
        dest_path = posixpath.normpath(posixpath.join(self.current_path, dest)) if not dest.startswith("/") else dest

        src_dir = self.navigate_to_path(posixpath.dirname(src_path))
        dest_dir = self.navigate_to_path(posixpath.dirname(dest_path))

        if src_dir is None or dest_dir is None:
            return f"Error: source or destination path not found"

        src_name = posixpath.basename(src_path)
        dest_name = posixpath.basename(dest_path)

        if src_name not in src_dir:
            return f"Error: source '{src_path}' not found"

        print(f"Source: {src_path}, Destination: {dest_path}")

        if isinstance(src_dir[src_name], dict):
            dest_dir[dest_name] = src_dir[src_name].copy()
        else:
            dest_dir[dest_name] = None

        self.cp_in_tar(src_path, dest_path)

        self.log_action("cp", f"{src} -> {dest}")
        return ""

    def navigate_to_path(self, path):
        """Переход к директории по пути."""
        current = self.fs
        print(f"Current FS: {current}")
        if path == "/":
            return current
        for part in path.strip("/").split("/"):
            if part in current and isinstance(current[part], dict):
                current = current[part]
            else:
                return None
        return current


class ShellGUI:
    def __init__(self, emulator):
        self.emulator = emulator
        self.window = tk.Tk()
        self.window.title(f"Shell - {emulator.hostname}")
        self.window.resizable(False, False)
        self.create_widgets()

    def create_widgets(self):
        self.output = tk.Text(self.window, height=20, width=80)
        self.output.pack()
        self.output.config(state=tk.DISABLED)

        self.input_field = tk.Entry(self.window, width=80)
        self.input_field.pack()
        self.input_field.bind("<Return>", self.execute_command)

    def execute_command(self, event):
        command = self.input_field.get()
        self.input_field.delete(0, tk.END)
        output = ""
        if command.startswith("ls"):
            self.output.config(state=tk.NORMAL)
            output = self.emulator.ls()
        elif command.startswith("cd"):
            self.output.config(state=tk.NORMAL)
            args = command.split()
            output = self.emulator.cd(args[1]) if len(args) > 1 else "Error: specify path."
        elif command.startswith("cp"):
            self.output.config(state=tk.NORMAL)
            args = command.split()
            if len(args) < 3:
                output = "Error: specify source and destination paths."
            else:
                output = self.emulator.cp(args[1], args[2])
        elif command.startswith("clear"):
            command = ""
            self.output.config(state=tk.NORMAL)
            self.output.delete("1.0", tk.END)
        elif command.startswith("exit"):
            self.window.quit()
        else:
            self.output.config(state=tk.NORMAL)
            output = f"{command}: command not found"

        self.output.insert(tk.END, f"{self.emulator.hostname}:{self.emulator.current_path}$ {command}\n{output}\n")
        self.output.config(state=tk.DISABLED)
        self.output.see(tk.END)

    def run(self):
        self.window.mainloop()


def main():
    parser = argparse.ArgumentParser(description="Shell Emulator")
    parser.add_argument("--hostname", required=True, help="Hostname")
    parser.add_argument("--vfs", required=True, help="Path to VFS tar archive")
    parser.add_argument("--log", required=True, help="Path to log file")
    args = parser.parse_args()

    emulator = ShellEmulator(args.hostname, args.vfs, args.log)
    gui = ShellGUI(emulator)
    gui.run()


if __name__ == "__main__":
    main()
