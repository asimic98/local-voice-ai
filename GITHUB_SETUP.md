# Kako napraviti novi GitHub repo i deploy-ovati projekat

## 1. Kreiraj novi repozitorijum na GitHub-u

1. Otvori **https://github.com/new**
2. **Repository name:** npr. `local-voice-ai` (ili kako želiš)
3. Opis (opciono)
4. Izaberi **Public**
5. **Ne** čekiraj "Add a README" – projekat već ima fajlove
6. Klikni **Create repository**

Kopiraj URL repozitorijuma (npr. `https://github.com/TVOJ_USERNAME/local-voice-ai.git`).

---

## 2. Inicijalizuj Git i push-uj kod

U terminalu (PowerShell) u folderu projekta pokreni:

```powershell
cd C:\Users\PC\Desktop\local-voice-ai

# Inicijalizuj Git
git init

# Dodaj sve fajlove ( .env je već u .gitignore )
git add .

# Prvi commit
git commit -m "Initial commit: local voice AI project"

# Glavna grana (ako GitHub očekuje 'main')
git branch -M main

# Poveži sa tvojim GitHub repo – ZAMENI sa svojim URL-om!
git remote add origin https://github.com/TVOJ_USERNAME/IME_REPO.git

# Push na GitHub
git push -u origin main
```

**Zameni** `TVOJ_USERNAME` i `IME_REPO` svojim GitHub korisničkim imenom i imenom repozitorijuma.

---

## 3. Ako koristiš GitHub CLI (`gh`)

Ako imaš [GitHub CLI](https://cli.github.com/) instaliran:

```powershell
cd C:\Users\PC\Desktop\local-voice-ai
git init
git add .
git commit -m "Initial commit: local voice AI project"
git branch -M main
gh repo create local-voice-ai --public --source=. --remote=origin --push
```

Ovo kreira **public** repo pod nazivom `local-voice-ai` i odmah push-uje kod.

---

## Napomena

- Fajl **`.env`** je u `.gitignore` – neće biti u repozitorijumu (dobro za tokene i tajne).
- Ako GitHub zatraži login, koristi Personal Access Token umesto lozinke ako imaš 2FA.
