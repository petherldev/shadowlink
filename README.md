# ShadowLink

ShadowLink is a **powerful, lightweight, and terminal-based URL masking tool** designed for ethical use in cybersecurity demonstrations, phishing awareness training, and red teaming exercises.

It allows you to **generate deceptive but legitimate-looking URLs** by masking original links with custom domains and keywords—perfect for simulating real-world phishing behavior in a controlled environment.


##  Features

- Mask any valid URL with a custom domain and keyword.
- Uses **multiple shorteners** (TinyURL, da.gd, clck.ru, osdb.link).
- Built-in validation for URLs, domains, and keywords.
- Animated loading spinner with polished CLI output.
- Works flawlessly on **Linux terminals**.
- Clean and single-file implementation for easy use.


## Installation

We **recommend using a Python virtual environment (venv)** to isolate dependencies.

### Step-by-step Setup

```bash
# 1. Clone the repo
git clone https://github.com/petherl/shadowlink.git
cd shadowlink

# 2. Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip3 install -r requirements.txt

# 4. Run the tool
python3 shadowlink.py
```


### Install via PyPI (Recommended)

If you prefer to install and use ShadowLink globally:

```bash
pip3 install shadowlink
```

Then run it from anywhere in your terminal:

```bash
shadowlink
```

Or using the Python module syntax:

```bash
python -m shadowlink
```

> 💡 This is the easiest way to use ShadowLink if you don’t want to clone the repository manually.


## Usage

Simply follow the on-screen prompts:

```bash
➤ Enter the original URL (e.g. https://example.com)
➤ Enter a custom domain (e.g. x.com)
➤ Enter a phishing keyword (e.g. login, signup, verify)
```

ShadowLink will then generate **multiple masked URLs** using various shortening services.

---

## Requirements

- Python 3.10+
- Linux or WSL terminal
- Internet connection (for link shortening)

---

> [!CAUTION]
>
> This tool is developed **strictly for educational and ethical purposes** such as:
> - Cybersecurity training
> - Social engineering awareness
> - Red team operations
>
> Any misuse of this tool for malicious purposes is **strongly discouraged and illegal**. The author is not responsible for any misuse or damage caused.


## Author

- **HErl**
- [https://github.com/petherl](https://github.com/petherl)
- [petherl@protonmail.com](mailto:petherl@protonmail.com)


## License

This project is released under the [MIT License](LICENSE).
