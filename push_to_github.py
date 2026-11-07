"""
CYBERAI - Push Repository to GitHub Helper Script
Usage:
    py push_to_github.py <github_repo_url_or_token>
Examples:
    py push_to_github.py https://github.com/username/cyberai.git
    py push_to_github.py https://<TOKEN>@github.com/username/cyberai.git
"""
import sys
import os
from pathlib import Path
from dulwich import porcelain
from dulwich.repo import Repo

BASE_DIR = Path(__file__).resolve().parent

def push_repo(remote_url: str):
    repo = Repo(str(BASE_DIR))
    print(f"[*] Repozitoriy: {BASE_DIR}")
    print(f"[*] GitHub masofaviy manzili: {remote_url}")

    # Set master or main branch
    head_ref = repo.head()
    print(f"[*] HEAD commit: {head_ref.decode('ascii')}")

    try:
        # Check if remote 'origin' exists, else add
        config = repo.get_config()
        config.set(("remote", "origin"), "url", remote_url.encode('utf-8'))
        config.write_to_path()
        print("[*] 'origin' masofaviy manzili muvaffaqiyatli ulandi.")

        print("[*] GitHub-ga push qilinmoqda...")
        porcelain.push(repo, remote_url, refspecs=[b"HEAD:refs/heads/main"])
        print("[+] Muvaffaqiyatli GitHub-ga yuklandi (Pushed to main branch)!")
    except Exception as e:
        print(f"[-] Xatolik yuz berdi: {str(e)}")
        print("\n[Tavsiya]: Agar autentifikatsiya xatosi bersa, quyidagicha URL formatida bering:")
        print("py push_to_github.py https://<GITHUB_PERSONAL_ACCESS_TOKEN>@github.com/<USERNAME>/cyberai.git")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        url = input("GitHub repozitoriy havolasini kiriting (https://github.com/username/cyberai.git): ").strip()
    else:
        url = sys.argv[1].strip()

    if url:
        push_repo(url)
    else:
        print("[-] URL kiritilmadi.")
