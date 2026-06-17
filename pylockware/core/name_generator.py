"""
Simple Name Generator Module for PyLockWare
Provides random name generation with configurable character sets
"""
import random
import string


class NameGenerator:
    def __init__(self, char_set='english'):
        """
        Initialize the name generator with a specific character set.
        
        Args:
            char_set: Character set to use ('english', 'chinese', 'mixed', 'numbers', 'hex')
        """
        self.char_sets = {
            'english': string.ascii_letters + string.digits,
            'chinese': ''.join(chr(i) for i in range(0x4E00, 0x9FFF)),  # Basic Chinese characters
            'mixed': string.ascii_letters + string.digits + ''.join(chr(i) for i in range(0x4E00, 0x9FFF)),
            'numbers': string.digits,
            'hex': string.hexdigits,
            'ascii': string.printable.strip(), # All printable ASCII except whitespace
            'l-i': "IliL"
        }
        
        self.char_set = self.char_sets.get(char_set, self.char_sets['english'])

    def generate_name(self, prefix='') -> str:
        """
        Generate a random name with the specified prefix.
        Ensures the name starts with a letter or underscore (valid Python identifier).

        Args:
            prefix: Prefix to add to the random name

        Returns:
            Randomly generated name
        """
        length = 128  # Default length
        
        # If prefix is empty or doesn't start with letter/underscore, add underscore
        if not prefix or (prefix[0] not in string.ascii_letters + '_'):
            prefix = '_' + prefix
        
        random_part = ''.join(random.choice(self.char_set) for _ in range(length))
        return f"{prefix}{random_part}"

    def set_char_set(self, char_set):
        """
        Change the character set used for name generation.
        
        Args:
            char_set: Character set to use ('english', 'chinese', 'mixed', 'numbers', 'hex')
        """
        self.char_set = self.char_sets.get(char_set, self.char_sets['english'])


# Convenience function for backward compatibility
def generate_random_name(prefix='', char_set='english') -> str:
    """
    Generate a random name with the specified prefix and character set.
    Uses a default length of 32 characters.
    
    Args:
        prefix: Prefix to add to the random name
        char_set: Character set to use ('english', 'chinese', 'mixed', 'numbers', 'hex')
        
    Returns:
        Randomly generated name
    """
    generator = NameGenerator(char_set)
    return generator.generate_name(prefix)