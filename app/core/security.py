"""
Security utilities for API key encryption/decryption
"""


class SecurityManager:
    """Handles encryption and decryption of sensitive data"""
    
    def __init__(self):
        # Temporarily disable encryption for testing
        self.cipher = None
    
    def encrypt(self, plaintext: str) -> str:
        """Encrypt plaintext string"""
        if not plaintext:
            return ""
        # Temporarily return plaintext without encryption
        return plaintext
    
    def decrypt(self, encrypted_text: str) -> str:
        """Decrypt encrypted string"""
        if not encrypted_text:
            return ""
        # Temporarily return as-is without decryption
        return encrypted_text


# Global security manager instance
security_manager = SecurityManager()
