# remote-vm
- Automate VM creation and forward SSH access through shortcut.

### Prerequisites
On `Windows`:
- [Python](https://www.microsoft.com/store/productId/9NCVDN91XZQP?ocid=pdpshare)
- [Git](https://git-scm.com/download/win)
- [VirtualBox](https://www.virtualbox.org/wiki/Downloads) \
    Update `Environment Variables` (in `System Properties`): \
    `C:\Program Files\Oracle\VirtualBox`

Optional:
- [Powershell](https://github.com/PowerShell/PowerShell?tab=readme-ov-file#get-powershell)
- [Windows Terminal](https://aka.ms/terminal)
- [Visual Studio Code](https://code.visualstudio.com/docs/?dv=win64user)

### Usage
1. Clone this repository:
    ```powershell
    git clone https://github.com/vaddern/remote-vm.git --depth=1 $HOME\remote-vm
    cd $HOME\remote-vm
    ```

1. Check [./config.json](./config.json) file first.
1.
    ```powershell
    python3 ./main.py -c create
    # it will open GUI with Debian installer
    # hints (optional):
    # - during install minimal debian:
    #    mark only `SSH server` and `Standard system utilities`
    ```
1.
    ```powershell
    python3 ./main.py -c forwardSSH
    ```
1. Check the SSH connection using shortcut: `ssh <ssh:alias from config.json>`.\
    E.g. `ssh deb`

1.  You can use commands like run, stop, remove, e.g. More info:
    ```powershell
    python3 ./main.py -h
    ```

### Optional inside VM:
1. Install sudo and add user to sudoers.
    ```bash
    su
    apt install -y sudo
    /sbin/adduser user sudo
    (logout)
    ```

### References
- https://andreafortuna.org/2019/10/24/how-to-create-a-virtualbox-vm-from-command-line/
