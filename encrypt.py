import os
import sys
import time
import struct
import hashlib
import random
from shutil import get_terminal_size
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers.algorithms import ChaCha20
from colorama import init, Fore, Style
init(autoreset=True)

ACCENT = Style.BRIGHT + Fore.MAGENTA
PRIMARY = Style.BRIGHT + Fore.CYAN
SUCCESS = Style.BRIGHT + Fore.GREEN
ERROR = Style.BRIGHT + Fore.RED
INFO = Style.BRIGHT + Fore.YELLOW
MUTED = Style.DIM + Fore.WHITE

BANNER_COLORS = [Fore.MAGENTA, Fore.CYAN, Fore.BLUE, Fore.MAGENTA, Fore.CYAN]

BANNER_ART = """⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡘⢧⡀⠀⠀⢰⣶⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡾⠁⠀⠙⢦⡀⢸⡏⠻⢦⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣣⡆⠀⠀⠀⠙⠺⡇⠀⠀⠙⠳⠦⡀⠀⠀⠀⠀⠀⠀⠀⣀⣀⣀⣠⠤⢤⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⡇⠀⠿⠒⠦⠴⠒⠓⠂⠀⠀⠀⠀⠀⠐⠒⠚⠛⠋⠉⠉⠉⠁⠀⠀⠀⠀⠉⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⠛⢦⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣴⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⠀⠀⠙⠛⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⣏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⠀⠀⠀⠀⠀⢀⣠⣄⡀⠀⠀⠀⠀⢀⣠⣤⣤⣀⠀⠀⠀⠀⠀⠀⠀⠀⣸⠇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⠃⠀⠀⠀⣰⠏⢉⣼⣧⠀⠀⠀⢠⣿⣅⠀⠀⢹⡆⠀⠀⠀⠀⠀⠀⢠⡏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡯⠀⢸⣿⣿⠀⠀⠀⣾⣿⣿⠀⠀⠀⣷⠀⠀⠀⠀⠀⢀⡞⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡴⠛⠁⢀⠈⠁⠀⢸⣿⣿⠀⠀⠀⢹⣿⣿⠀⠀⠀⠉⠀⠀⠀⠈⠛⢿⡅⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⢿⡀⠀⠀⢸⣧⣴⣀⣄⠉⣁⠐⣳⢀⣨⣟⠋⠀⠀⣀⣴⣠⠀⠀⠀⢀⡼⠃⠀⠀⠀⢰⣤⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠛⢶⡎⢳⣌⡉⠀⠀⠙⠻⣯⣉⢉⣿⠄⠀⠀⢉⣬⡿⠃⠀⠀⢾⡀⠀⠀⠀⠀⣸⠃⠙⠳⣤⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣇⣀⡈⠙⠛⢳⡶⣤⣤⣭⣽⣭⡴⣶⠛⣿⣥⡄⢠⣤⣤⣼⡇⠀⡄⣾⠀⣿⠀⠀⠀⠀⠙⢦⡄⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢰⡟⠛⠺⠷⢤⣤⣿⣿⣿⣤⡾⠟⣃⡿⠀⠀⠀⠀⠀⠀⠘⠃⡿⢀⡗⠀⠀⠀⠀⠀⠈⢻⣆⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢻⣆⠀⠀⠀⢸⣏⣌⡙⡇⠀⠀⠺⣦⠀⠀⠀⠀⠀⠀⣼⣄⠀⢸⡇⠀⠀⠀⠀⠀⠀⠀⠹⣇⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢙⣷⠀⠀⠀⠛⠛⠛⠁⠀⠀⣾⠁⠀⠀⠀⠀⠀⢰⡟⢹⣆⡿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠹⣆⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢰⡏⠁⠀⠀⠀⠀⣤⠀⠀⠀⢰⣾⠀⠀⠀⠀⠀⣠⡟⠀⠀⠿⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢿⡀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠉⡟⠛⠛⠀⣠⡟⠀⠀⠀⢸⢹⡄⠀⠀⢀⡴⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠸⡇⣿⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⠀⠀⠀⣿⡇⠀⠀⠀⢸⠸⣇⣀⡴⠋⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡇⢻⠀⡄
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣰⣿⠀⠀⠀⣿⠀⠀⠀⠀⣿⠀⠻⣏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⡇⢼⣰⡇
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡶⠶⠛⠋⣿⠀⠀⢠⡏⠀⠀⠀⠀⡿⠀⠀⠙⢷⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣼⢁⡿⠾⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣠⣤⠿⠀⠀⠀⣿⠀⠀⣸⠃⠀⠀⠀⢠⡏⠀⠀⠀⠀⢹⡷⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⠟⠈⠁⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠰⣟⠁⠀⠀⠀⠀⢶⣿⠀⢠⡟⠀⠀⠀⠀⢸⠅⠀⠀⠀⠀⢻⡆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⡾⠋⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡾⠃⠀⠀⠀⠀⠘⣿⢀⡾⠁⠀⠀⠀⠀⣿⠀⠀⠀⠀⣴⠟⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠉⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⢀⣴⠿⢦⣄⡀⠀⠀⠀⠀⡏⣼⠃⠀⠀⠀⠀⢀⡿⠀⠀⠀⠀⢹⡇⠀⠀⠀⠀⠀⠀⠀⠀⢠⣄⣀⣀⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⢀⣴⠟⠓⠤⡀⠈⠹⣦⡀⠀⠐⣷⣷⡇⠀⢠⡄⠀⣼⣃⣀⣀⣀⠀⠀⡇⠀⠀⠀⠲⣄⡀⠀⠀⠀⣈⡽⠟⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⣠⠿⠅⣀⠀⠀⠈⠳⡄⠸⣧⠀⣠⡿⠿⢷⢤⣬⣿⡾⠛⠉⠉⠉⠉⠷⣴⡇⠀⠀⠀⠀⠈⠙⠛⠛⠛⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⣠⡾⢁⡀⠀⠀⠑⢄⠀⠀⠸⣄⣿⠟⠉⠀⠀⠀⠀⠀⢸⣇⠤⠤⠦⠤⠤⢀⣹⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⢀⣴⠋⠀⠀⠈⠑⢄⠀⠀⢣⠀⣠⡟⠁⠀⠀⠀⠀⠀⠀⠀⢸⠇⠀⠀⠀⠀⠀⠀⠉⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⢰⡏⣴⠉⠑⣢⣄⠀⠀⢳⣀⣴⠟⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⣸⡀⠀⠀⠀⠀⠀⠀⠀⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠈⠿⣏⠀⠀⢿⠀⣳⣤⡶⠛⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⣀⣀⡀⠀⠀⠀⠀⢹⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠋⠙⠛⠛⠛⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⠀⠀⠀⠀⠉⠓⠢⣼⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⣀⠀⣀⣀⡀⠀⣸⡟⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⣿⢰⡇⠀⠀⢿⢑⡿⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢿⣷⣀⣤⣼⡿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀"""


def terminal_width():
    size = get_terminal_size((100, 20))
    return size.columns if hasattr(size, "columns") else size[0]


def print_divider(color=Fore.CYAN, pattern="═"):
    width = terminal_width()
    print(f"{Style.BRIGHT}{color}{pattern * width}{Style.RESET_ALL}")


def render_banner():
    lines = BANNER_ART.splitlines()
    colored_lines = []
    for idx, line in enumerate(lines):
        color = BANNER_COLORS[idx % len(BANNER_COLORS)]
        colored_lines.append(f"{Style.BRIGHT}{color}{line}{Style.RESET_ALL}")
    return "\n".join(colored_lines)

def clear_screen():
    if os.name == "posix":
        os.system("clear")
    elif os.name in ("nt", "dos", "ce"):
        os.system("cls")


def print_header():
    print()
    print_divider(Fore.MAGENTA)
    print(render_banner())
    print_divider(Fore.MAGENTA)
    print(
        f"{PRIMARY}MaggiCrypt CLI  {Fore.WHITE}•  {INFO}System Time:"
        f" {Fore.WHITE}{time.strftime('%Y-%m-%d %H:%M:%S')}"
    )
    print(
        f"{MUTED}Multi-layer AES + ChaCha20 protection · Use -e to encrypt,"
        f" -d to decrypt · or run without flags for interactive mode"
    )
    print_divider(Fore.MAGENTA)
    print()

def create_directories():
    dirs = ['encrypted', 'decrypted']
    for d in dirs:
        os.makedirs(d, exist_ok=True)
    directory_status = ', '.join(dirs)
    print(f"{ACCENT}⟡ Directories ready:{Fore.WHITE} {directory_status}")

def transform_key(base_key):
    hash_key = hashlib.sha512(base_key).digest()
    transformed = bytes(b ^ 0xA5 for b in hash_key)
    final_key = transformed[:48]
    return final_key[:16], final_key[16:48]

def generate_dynamic_nonce(file_data, length=12):
    h = hashlib.sha256(file_data).digest()[:length]
    random_part = os.urandom(length)
    return bytes(a ^ b for a, b in zip(h, random_part))

def add_padding(data):
    pad = os.urandom(16)
    return pad + data + pad

def remove_padding(data):
    return data[16:-16]

def multi_round_encrypt(data, key1, key2, aes_nonce, chacha_nonce):
    backend = default_backend()
    # AES-GCM Verschlüsselung
    cipher_aes = Cipher(algorithms.AES(key1), modes.GCM(aes_nonce), backend)
    encryptor_aes = cipher_aes.encryptor()
    aes_ct = encryptor_aes.update(data) + encryptor_aes.finalize()
    tag = encryptor_aes.tag

    # ChaCha20 Verschlüsselung
    chacha_cipher = Cipher(ChaCha20(key2, chacha_nonce), mode=None, backend=backend)
    encryptor_chacha = chacha_cipher.encryptor()
    final_ct = encryptor_chacha.update(aes_ct) + encryptor_chacha.finalize()

    return final_ct, tag

def multi_round_decrypt(final_ct, key1, key2, aes_nonce, chacha_nonce, tag):
    backend = default_backend()
    # ChaCha20 Entschlüsselung
    chacha_cipher = Cipher(ChaCha20(key2, chacha_nonce), mode=None, backend=backend)
    decryptor_chacha = chacha_cipher.decryptor()
    aes_ct = decryptor_chacha.update(final_ct) + decryptor_chacha.finalize()
    # AES-GCM Entschlüsselung
    cipher_aes = Cipher(algorithms.AES(key1), modes.GCM(aes_nonce, tag), backend)
    decryptor_aes = cipher_aes.decryptor()
    return decryptor_aes.update(aes_ct) + decryptor_aes.finalize()

def obfuscate_data(data):
    r = random.randint(1, 255)
    return bytes(b ^ r for b in data), r

def deobfuscate_data(data, r):
    return bytes(b ^ r for b in data)

def check_debugger():
    if sys.gettrace():
        print(f"{ERROR}Debugger detected! Exiting.")
        sys.exit(1)

def encrypt_file(input_path):
    try:
        import threading
        import itertools
        import sys as sys_module

        check_debugger()
        print(f"\n{PRIMARY}⚙  Encryption Process Initiated")
        print_divider(Fore.CYAN, pattern="─")

        # Spinner animation setup
        spinner_running = True

        def spinner():
            for c in itertools.cycle(['|', '/', '-', '\\']):
                if not spinner_running:
                    break
                sys_module.stdout.write(
                    f"\r{PRIMARY}Encrypting {Fore.WHITE}✶ {Fore.CYAN}{c}{Style.RESET_ALL}  "
                )
                sys_module.stdout.flush()
                time.sleep(0.1)
            sys_module.stdout.write('\r' + ' ' * 40 + '\r')

        spinner_thread = threading.Thread(target=spinner)
        spinner_thread.start()

        # Generiere einen zufälligen Basis-Schlüssel (32 Byte)
        base_key = os.urandom(32)
        key_part1, key_part2 = transform_key(base_key)

        with open(input_path, 'rb') as f:
            file_data = f.read()

        aes_nonce = generate_dynamic_nonce(file_data, 12)
        chacha_nonce = generate_dynamic_nonce(file_data, 16)

        key_mixing_material = hashlib.sha256(aes_nonce).digest()[:16]
        mixed_key1 = bytes(a ^ b for a, b in zip(key_part1, key_mixing_material))

        padded_data = add_padding(file_data)
        ct_round, tag = multi_round_encrypt(
            padded_data, mixed_key1, key_part2, aes_nonce, chacha_nonce
        )

        spinner_running = False
        spinner_thread.join()

        obf_ct, xor_val = obfuscate_data(ct_round)

    
        header_key = base_key

        # Aufbau des finalen Payload:
        # fake_header (8B) + header_key (32B) + aes_nonce (12B) +
        # chacha_nonce (16B) + tag (16B) + xor_val (1B) + obf_ct (Rest)
        fake_header = b'\x89PNG\r\n\x1a\n'
        final_payload = (
            header_key +
            aes_nonce +
            chacha_nonce +
            tag +
            struct.pack('B', xor_val) +
            obf_ct
        )
        full_data = fake_header + final_payload

        filename = os.path.basename(input_path) + '.femboycrypt'
        output_path = os.path.join('encrypted', filename)
        with open(output_path, 'wb') as f:
            f.write(full_data)

        print(f"\n{SUCCESS}✔ Encryption complete!{Fore.WHITE} Saved to {output_path}")
        print_divider(Fore.CYAN)
        return output_path

    except Exception as e:
        print(f"\n{ERROR}✖ Encryption failed:{Fore.WHITE} {str(e)}")
        sys.exit(1)

def decrypt_file(input_path):
    try:
        check_debugger()
        print(f"\n{PRIMARY}🔐  Decryption Process Initiated")
        print_divider(Fore.CYAN, pattern="─")

        with open(input_path, 'rb') as f:
            full_data = f.read()

        # Entferne den Fake-Header (8 Byte)
        if full_data.startswith(b'\x89PNG\r\n\x1a\n'):
            payload = full_data[8:]
        else:
            payload = full_data

        # Zerlege den Payload gemäß obigem Aufbau
        # header_key (32B) + aes_nonce (12B) + chacha_nonce (16B) + tag (16B) + xor_val (1B) + obf_ct (Rest)
        header_key = payload[:32]
        aes_nonce = payload[32:44]
        chacha_nonce = payload[44:60]
        tag = payload[60:76]
        xor_val = payload[76]
        obf_ct = payload[77:]

        # Nutze den aus der Datei extrahierten Basis-Schlüssel
        base_key = header_key
        key_part1, key_part2 = transform_key(base_key)
        key_mixing_material = hashlib.sha256(aes_nonce).digest()[:16]
        mixed_key1 = bytes(a ^ b for a, b in zip(key_part1, key_mixing_material))

        ct_round = deobfuscate_data(obf_ct, xor_val)
        padded_data = multi_round_decrypt(
            ct_round, mixed_key1, key_part2, aes_nonce, chacha_nonce, tag
        )

        original_data = remove_padding(padded_data)
        base_name = os.path.basename(input_path)
        if base_name.endswith('.femboycrypt'):
            base_name = base_name[: -len('.femboycrypt')]
        elif base_name.endswith('.enc'):
            base_name = base_name[: -len('.enc')]
        output_filename = base_name + '.decrypted'
        output_path = os.path.join('decrypted', output_filename)
        with open(output_path, 'wb') as f:
            f.write(original_data)

        print(f"\n{SUCCESS}✔ Decryption complete!{Fore.WHITE} File restored at {output_path}")
        print_divider(Fore.CYAN)
        return output_path

    except Exception as e:
        print(f"\n{ERROR}✖ Decryption failed:{Fore.WHITE} {str(e)}")
        sys.exit(1)


def prompt_user_action():
    print(
        f"{INFO}No CLI arguments detected — switching to interactive mode.{Style.RESET_ALL}"
    )
    while True:
        try:
            choice = input(
                f"{PRIMARY}Choose action [{Fore.WHITE}encrypt{PRIMARY}/{Fore.WHITE}decrypt{PRIMARY}]: "
                f"{Style.RESET_ALL}"
            )
        except (EOFError, KeyboardInterrupt):
            print(f"\n{ERROR}Operation cancelled by user.")
            sys.exit(1)

        if not choice:
            print(f"{ERROR}Please enter 'encrypt' or 'decrypt'.")
            continue

        choice = choice.strip().lower()
        if choice in ("encrypt", "e"):
            return "-e"
        if choice in ("decrypt", "d"):
            return "-d"

        print(f"{ERROR}Unrecognized option '{choice}'. Please choose encrypt or decrypt.")


def prompt_file_path(action):
    verb = "encrypt" if action == "-e" else "decrypt"
    while True:
        try:
            path = input(
                f"{PRIMARY}Enter the file path to {verb}:{Fore.WHITE} "
                f"{Style.RESET_ALL}"
            )
        except (EOFError, KeyboardInterrupt):
            print(f"\n{ERROR}Operation cancelled by user.")
            sys.exit(1)

        path = path.strip().strip('"').strip("'")
        if not path:
            print(f"{ERROR}File path cannot be empty. Please try again.")
            continue

        if os.path.isfile(path):
            if action == "-d" and not path.lower().endswith('.femboycrypt'):
                print(
                    f"{INFO}Note:{Fore.WHITE} The expected encrypted extension is "
                    f".femboycrypt, but proceeding with the provided file.{Style.RESET_ALL}"
                )
            return path

        print(f"{ERROR}File not found:{Fore.WHITE} {path}. Please try again.")


if __name__ == "__main__":
    clear_screen()
    print_header()
    create_directories()

    if len(sys.argv) == 3 and sys.argv[1] in ['-e', '-d']:
        action = sys.argv[1]
        file_path = sys.argv[2]
    elif len(sys.argv) == 1:
        action = prompt_user_action()
        file_path = prompt_file_path(action)
    else:
        print(
            f"{INFO}Usage:{Fore.WHITE} python encrypt.py "
            f"{PRIMARY}-e{Fore.WHITE}/{PRIMARY}-d {Fore.WHITE}[file]"
        )
        print(f"{INFO}Tip:{Fore.WHITE} Run without any arguments for interactive mode.")
        sys.exit(1)

    if action == '-e':
        encrypt_file(file_path)
    elif action == '-d':
        decrypt_file(file_path)
