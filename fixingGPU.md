## Fix NVIDIA driver — kernel/module mismatch

### Symptom
- `nvidia-smi` fails: "couldn't communicate with the NVIDIA driver"
- Ollama runs on CPU (very slow)

### Root cause
Running kernel `6.17.0-29-generic` has no matching NVIDIA kernel module
installed. The newest installed module is for kernel `6.17.0-23-generic`.
The matching package `linux-modules-nvidia-595-open-6.17.0-29-generic`
exists in the apt repos but was never pulled in.

### Fix (run as sudo)

# 1. Install the missing module for the current kernel
sudo apt update
sudo apt install linux-modules-nvidia-595-open-6.17.0-29-generic

# 2. Try to load the module without rebooting
sudo modprobe nvidia

# 3. Verify
nvidia-smi
# Expected: GPU info table (model, driver version, memory, processes).

# 4. If modprobe failed (kernel sometimes refuses fresh modules), reboot:
sudo reboot

# 5. After GPU is back, restart Ollama so it picks up the GPU
sudo systemctl restart ollama
# or however ollama is launched on this machine

### Optional cleanup (do AFTER the fix is confirmed working)

# Remove the orphan older driver metapackage
sudo apt autoremove --purge nvidia-driver-590-open

# Remove old unused kernels (keep the running one + 1 fallback)
sudo apt autoremove --purge
