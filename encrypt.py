import os
import sys
import time
import struct
import hashlib
import random
from shutil import get_terminal_size
from tqdm import tqdm
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers.algorithms import ChaCha20
from colorama import init, Fore, Style
init(autoreset=True)

BANNER = fr"""
{Fore.CYAN}$$$$$$$\\   $$\\     $$\\ $$$$$$$$\\  $$$$$$\\  
$$  __$$\\  $$ |    $$ |\\__$$  __|$$  __$$\\ 
$$ |  $$ | $$ |    $$ |   $$ |   $$ /  \\__|
$$$$$$$  | $$ |    $$ |   $$ |   \\$$$$$$\\  
$$  ____/  $$ |    $$ |   $$ |    \\____$$\\ 
$$ |       $$ |    $$ |   $$ |   $$\\   $$ |
$$ |       \\$$$$$$$  |   $$ |   \\$$$$$$  |
\\__|        \\_______/    \\__|    \\______/
{Fore.GREEN}Advanced File Encryption v3.0{Style.RESET_ALL}
"""

def clear_screen():
    if os.name == "posix":
        os.system("clear")
    elif os.name in ("nt", "dos", "ce"):
        os.system("cls")

def print_header():
    cols, _ = get_terminal_size()
    print("\n" + "=" * cols)
    print(BANNER)
    print(f"{Fore.YELLOW}System Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * cols + "\n")

def create_directories():
    dirs = ['encrypted', 'decrypted']
    for d in dirs:
        os.makedirs(d, exist_ok=True)
    print(f"{Fore.MAGENTA}» Directory check: {dirs} ready")

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
        print(f"{Fore.RED}Debugger detected! Exiting.")
        sys.exit(1)

def encrypt_file(input_path):
    try:
        import threading
        import itertools
        import sys as sys_module

        check_debugger()
        print(f"\n{Fore.WHITE}[{Fore.BLUE}ENCRYPTION PROCESS{Fore.WHITE}]")
        print("-" * get_terminal_size().columns)

        # Spinner animation setup
        spinner_running = True

        def spinner():
            for c in itertools.cycle(['|', '/', '-', '\\']):
                if not spinner_running:
                    break
                sys_module.stdout.write(f'\r{Fore.CYAN}Encrypting... {c}')
                sys_module.stdout.flush()
                time.sleep(0.1)
            sys_module.stdout.write('\r' + ' ' * 20 + '\r')

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

        filename = os.path.basename(input_path) + '.enc'
        output_path = os.path.join('encrypted', filename)
        with open(output_path, 'wb') as f:
            f.write(full_data)

        print(f"\n{Fore.GREEN}✅ ENCRYPTION COMPLETE: {output_path}")
        print("=" * get_terminal_size().columns)
        return output_path

    except Exception as e:
        print(f"\n{Fore.RED}❌ ENCRYPTION FAILED: {str(e)}")
        sys.exit(1)

def decrypt_file(input_path):
    try:
        check_debugger()
        print(f"\n{Fore.WHITE}[{Fore.BLUE}DECRYPTION PROCESS{Fore.WHITE}]")
        print("-" * get_terminal_size().columns)

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
        output_filename = os.path.basename(input_path).replace('.enc', '') + '.decrypted'
        output_path = os.path.join('decrypted', output_filename)
        with open(output_path, 'wb') as f:
            f.write(original_data)

        print(f"\n{Fore.GREEN}✅ DECRYPTION COMPLETE: {output_path}")
        print("=" * get_terminal_size().columns)
        return output_path

    except Exception as e:
        print(f"\n{Fore.RED}❌ DECRYPTION FAILED: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    clear_screen()
    print_header()
    create_directories()

    if len(sys.argv) != 3 or sys.argv[1] not in ['-e', '-d']:
        print(f"{Fore.YELLOW}Usage: python encrypter.py -e [file] | -d [file]")
        sys.exit(1)

    action = sys.argv[1]
    file_path = sys.argv[2]

    if action == '-e':
        encrypt_file(file_path)
    elif action == '-d':
        decrypt_file(file_path)
