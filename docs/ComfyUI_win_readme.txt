#cu128 for 5060Ti-16G

cd ComfyUI_windows_portable

# Online

.\python_embeded\python.exe -m pip uninstall torch torchvision torchaudio

.\python_embeded\python.exe -m pip install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cu128



# Local

.\python_embeded\python.exe -m pip download --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cu128 -d .\pkgs

.\python_embeded\python.exe -m pip install --no-index --find-links=.\pkgs torch torchvision torchaudio
