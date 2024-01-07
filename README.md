# remote-vm
- Automate VM creation and forward SSH access through shortcut.

### Prerequisites
On `Windows`.\
Run it in `Powershell` as `Admin`:
```powershell
Set-ExecutionPolicy RemoteSigned  # revert: Restricted
```
Run it in `Powershell` as `User`:
```powershell
winget install --id=jazzdelightsme.WingetPathUpdater  -e
winget install --id Git.Git -e --source winget
winget install -e --id Oracle.VirtualBox
winget install -e --id Python.Python.3.12
winget install -e --id Microsoft.VisualStudioCode # optional
winget install -e --id Microsoft.WindowsTerminal # optional
```

### Usage
1. Clone this repository (in `Powershell` as `User`):
    ```powershell
    git clone https://github.com/anvoDark/remote-vm.git --depth=1 $HOME\remote-vm
    ```

1. Check [./config.json](./config.json) file first.
1.
    ```powershell
    python3 ./main.py -c create
    # hints (optional):
    # - install minimal debian: mark `SSH server` and `Standard system utilities` only
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

### References
- https://andreafortuna.org/2019/10/24/how-to-create-a-virtualbox-vm-from-command-line/
