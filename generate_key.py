from cryptography.fernet import Fernet

# Генерация ключа
key = Fernet.generate_key()
print("Сгенерированный ключ:", key)

# Сохраняем этот ключ и используйте его в audio_sender.py и audio_receiver.py
