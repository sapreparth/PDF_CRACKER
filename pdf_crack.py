from typing import Sequence
from itertools import product
import time
import pikepdf
import math
import numpy as np
from pikepdf import PasswordError

# Define constant alphabets and numeric sequences for password generation
ALPHABET_UPPERCASE: Sequence[str] = tuple('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
ALPHABET_LOWERCASE: Sequence[str] = tuple('abcdefghijklmnopqrstuvwxyz')
NUMBER: Sequence[str] = tuple('0123456789')

def as_list(l):
    """
    Converts input into a list, if it is not already iterable.
    Handles list, tuple, set, and numpy array inputs.
    """
    if isinstance(l, (list, tuple, set, np.ndarray)):
        return list(l)
    return [l]

def human_readable_numbers(n: float, decimals: int = 0) -> str:
    """
    Converts a number into a human-readable format (e.g., 1,000 -> 1 thousand).
    """
    n = round(n)
    if n < 1000:
        return str(n)
    names = ['', 'thousand', 'million', 'billion', 'trillion', 'quadrillion']
    idx = max(0, min(len(names) - 1, int(math.log10(n) // 3)))
    return f'{n / 10**(3 * idx):.{decimals}f} {names[idx]}'

def check_password(pdf_file_path: str, password: str) -> bool:
    """
    Attempts to open the PDF file with the provided password.
    Returns True if successful, False otherwise.
    """
    try:
        with pikepdf.open(pdf_file_path, password=password):
            return True
    except PasswordError:
        return False

def check_passwords(pdf_file_path: str, combination: list, log_freq: int = int(1e4)) -> None:
    """
    Attempts to brute-force the password for the given PDF file by generating
    combinations of characters from the provided lists.

    Args:
        pdf_file_path: Path to the PDF file to unlock.
        combination: A list of sequences (e.g., alphabets, numbers) to generate passwords.
        log_freq: Frequency of logging progress during password attempts.
    """
    # Ensure all elements in the combination are lists
    combination = [tuple(as_list(c)) for c in combination]
    print(f'Trying all combinations: {combination}')

    # Calculate total number of possible passwords
    num_passwords: int = np.product([len(x) for x in combination])
    passwords = product(*combination)
    success: bool | str = False
    count: int = 0
    start: float = time.perf_counter()

    for password_tuple in passwords:
        password = ''.join(password_tuple)  # Convert tuple to string
        if check_password(pdf_file_path, password=password):
            success = password
            print(f'SUCCESS with password "{password}"')
            break

        count += 1
        if count % log_freq == 0:
            now = time.perf_counter()
            elapsed_time = now - start
            passwords_per_sec = count / elapsed_time
            print(f'Tried {human_readable_numbers(count)} ({100 * count / num_passwords:.1f}%) of '
                  f'{human_readable_numbers(num_passwords)} passwords in {elapsed_time:.3f} seconds '
                  f'({human_readable_numbers(passwords_per_sec)} passwords/sec). Latest password tried: "{password}"')

    end: float = time.perf_counter()
    total_time = end - start
    msg: str = f'Tried {count} passwords in {total_time:.3f} seconds ({count / total_time:.3f} passwords/sec). '
    msg += f"Correct password: {success}" if success else f"All {num_passwords} passwords failed."
    print(msg)

# Example usage (comment out in production):
# check_passwords("example.pdf", [ALPHABET_LOWERCASE, NUMBER], log_freq=10000)
