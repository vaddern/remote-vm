import os
import sys
import argparse
from pathlib import Path
import json
import urllib.request
import shutil

from tools import shell

IS_DEBUG = True
BASE_PATH = os.path.join(Path.home(), "remote-vm")
OUT_LOG = os.path.join(BASE_PATH, "out", "out.log")


class ControlVM:
    def __init__(self, configPath):
        self.readConfig(configPath)
        self.sshConfig = self.config["ssh"]
        self.vmConfig = self.config["vm"]
        self.manage = "VBoxManage "
        self.name = self.vmConfig["machine-name"]
        self.isoPath = os.path.join(
            BASE_PATH, "out", self.vmConfig["iso-out"])
        self.vmPath = os.path.join(BASE_PATH, "vm", self.name)

    def readConfig(self, configPath):
        print("Config path: " + configPath)
        with open(configPath) as f:
            self.config = json.load(f)
        if not self.config:
            print("Empty config file!")
            sys.exit()
        if IS_DEBUG:
            print(self.config)

    def execCommand(self, command, gui=False):
        cmd = f"{self.manage}"
        if command == "run":
            startType = "gui" if gui else "headless"
            cmd += f"startvm {self.name} --type {startType}"
        elif command == "stop":
            cmd += f"controlvm {self.name} savestate"
        elif command == "reboot":
            cmd += f"controlvm {self.name} reboot"
        else:
            print(f"Wrong command: {command}!")
            sys.exit()
        shell(cmd)

    def cleanVM(self, force=True):
        print(f"Deleting {self.name}")
        self.execCommand("stop")
        isForce = " --delete" if force else ""
        shell(f"{self.manage} unregistervm {self.name} {isForce}", OUT_LOG)
        shutil.rmtree(self.vmPath)

    def forwardSSH(self):
        sshHome = os.path.join(Path.home(), ".ssh")
        if not os.path.exists(sshHome):
            os.mkdir(sshHome)

        keyPath = os.path.join(sshHome, "id_rsa-remote-ssh")
        if not os.path.exists(keyPath):
            shell("ssh-keygen -t rsa -b 4096 -f" + keyPath)

        config = f"\nHost {self.sshConfig["alias"]}\n\t \
            User {self.sshConfig["login"]}\n\t \
            HostName {self.sshConfig["host"]}\n\t \
            Port {self.sshConfig["port"]}\n\t \
            IdentityFile {keyPath}\n \
            "

        configPath = os.path.join(sshHome, "config")
        if not os.path.exists(configPath):
            with open(configPath, "a") as f:
                f.write(config)

        pubKeyPath = keyPath + ".pub"
        if not os.path.exists(pubKeyPath):
            return

        userAtHost = self.sshConfig["login"] + "@" + self.sshConfig["host"]
        with open(pubKeyPath, "r") as f:
            pubKey = f.readline().replace("\n", "")
            print(pubKey)
            unixCommands = f"mkdir -p ~/.ssh && chmod 700 ~/.ssh \
                && echo '{pubKey}' >> ~/.ssh/authorized_keys && \
                    chmod 600 ~/.ssh/authorized_keys"

            print(unixCommands)
            cmd = f"ssh -p {self.sshConfig["port"]} \
                {userAtHost} \"{unixCommands}\""
            shell(cmd)

    def createVM(self):
        if not os.path.exists(self.isoPath):
            print("Downloading ISO to " + self.isoPath)
            urllib.request.urlretrieve(self.vmConfig["iso-url"], self.isoPath)

        memorySize = int(self.vmConfig["vmemSize"])
        commands = [
            # Create VM
            f"createvm --name {self.name} \
                --ostype {self.vmConfig["os-type"]} --register --basefolder {self.vmPath}",
            # Set memory and network
            f"modifyvm {self.name} --ioapic on",
            f"modifyvm {self.name} \
                --cpus {self.vmConfig["cpus"]} --memory {memorySize} --vram 128",
            f"modifyvm {self.name} --nic1 nat",
        ]
        vdi = os.path.join(self.vmPath, self.name + "_DISK.vdi")
        print(vdi)

        # Create Disk and connect Debian Iso
        diskSize = int(self.vmConfig["diskSize"])
        commands += [
            f"createhd --filename {vdi} --size {diskSize} --format VDI",
            f"storagectl {self.name} --name \"SATA Controller\" \
                --add sata --controller IntelAhci",
            f"storageattach {self.name} --storagectl \"SATA Controller\" \
                --port 0 --device 0 --type hdd --medium {vdi}",
        ]
        # Mount ISO
        commands += [
            f"storagectl {self.name} --name \"IDE Controller\" \
                --add ide --controller PIIX4",
            f"storageattach {self.name} --storagectl \"IDE Controller\" --port 1 --device 0 \
                --type dvddrive --medium {self.isoPath}",
            f"modifyvm {self.name} --boot1 dvd --boot2 disk \
                --boot3 none --boot4 none",
        ]
        # Setup SSH
        commands += [f"modifyvm {self.name} \
                     --natpf1 guestssh,tcp,,{self.sshConfig["port"]},,22"]
        for command in commands:
            command = self.manage + command
            print(command)
            shell(command, OUT_LOG)


def parseArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--configPath",
        help="config file path to this repo",
        default=os.path.join(BASE_PATH, "config.json"),
    )
    parser.add_argument(
        "--command", "-c", required=True,
        help="execute command to control VM",
        choices=["create", "remove", "run", "stop", "reboot", "forwardSSH"],
    )
    parser.add_argument(
        "--silent", "-s", help="silent", action="store_true", default=True
    )
    return parser.parse_args()


def main():
    args = parseArgs()
    if not args.configPath or not os.path.exists(args.configPath):
        print("Unable to load config! ", args.configPath)
        sys.exit()

    OUT_DIR = os.path.dirname(OUT_LOG)
    if not os.path.exists(OUT_DIR):
        os.makedirs(OUT_DIR)

    vm = ControlVM(args.configPath)

    if args.command == "create":
        vm.createVM()
        vm.execCommand("run", gui=True)
    elif args.command == "remove":
        vm.cleanVM()
    elif args.command == "forwardSSH":
        vm.forwardSSH()
    elif args.command == "run" and os.path.exists(vm.vmPath):
        vm.execCommand("run", gui=args.silent)
    elif args.command == "stop" or args.command == "reboot":
        vm.execCommand(args.command, gui=args.silent)


if __name__ == "__main__":
    main()
