# encode_fonts.py
import base64

def encode_font(filename):
    with open(filename, "rb") as f:
        return base64.b64encode(f.read()).decode()

print("REGULAR = '''")
print(encode_font("DejaVuSans.ttf"))
print("'''")

print("\nBOLD = '''")
print(encode_font("DejaVuSans-Bold.ttf"))
print("'''")