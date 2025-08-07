# Generated with CHATGPT

import torch
import open_clip
from PIL import Image
import easyocr
import re

device = "cuda" if torch.cuda.is_available() else "cpu"

model, _, preprocess = open_clip.create_model_and_transforms('ViT-B-32', pretrained='openai')
tokenizer = open_clip.get_tokenizer('ViT-B-32')

ocr_reader = easyocr.Reader(['en'], gpu=(device == 'cuda'))

nsfw_prompts = [
    "a Roblox avatar in sexualized clothing",
    "a Roblox avatar wearing lingerie",
    "a Roblox avatar dressed inappropriately for children"
]
safe_prompts = [
    "a Roblox avatar dressed in normal clothing",
    "a child-safe Roblox avatar"
]

flagged_keywords = [
    "erp", "hug me", "snowbunny", "daddy", "femboy", "add me", "condo", "roleplay",
    "toy", "furry", "fishnet", "fvta", "domme", "naked", "strip", "18+", "17+", "fembxy",
    "fmby", "fxmboy", "fxmby", "fxbxy", "studio"
]

MORSE_CODE_DICT = {
    '.-': 'A', '-...': 'B', '-.-.': 'C', '-..': 'D', '.': 'E',
    '..-.': 'F', '--.': 'G', '....': 'H', '..': 'I', '.---': 'J',
    '-.-': 'K', '.-..': 'L', '--': 'M', '-.': 'N', '---': 'O',
    '.--.': 'P', '--.-': 'Q', '.-.': 'R', '...': 'S', '-': 'T',
    '..-': 'U', '...-': 'V', '.--': 'W', '-..-': 'X', '-.--': 'Y',
    '--..': 'Z', '-----': '0', '.----': '1', '..---': '2', '...--': '3',
    '....-': '4', '.....': '5', '-....': '6', '--...': '7', '---..': '8',
    '----.': '9'
}

def decode_morse(morse_code):
    words = morse_code.strip().split('   ')  # 3 spaces separate words in morse
    decoded_words = []
    for word in words:
        letters = word.split()
        decoded_word = ''.join(MORSE_CODE_DICT.get(letter, '') for letter in letters)
        decoded_words.append(decoded_word)
    return ' '.join(decoded_words)

def find_morse_in_text(text):
    candidates = re.findall(r'[\.\-\s]{5,}', text)
    decoded = []
    for c in candidates:
        try:
            decoded_text = decode_morse(c)
            if len(decoded_text) > 2:
                decoded.append(decoded_text)
        except:
            continue
    return decoded

def rot_x(text, x):
    result = []
    for ch in text:
        if ch.isalpha():
            base = ord('A') if ch.isupper() else ord('a')
            shifted = chr((ord(ch) - base + x) % 26 + base)
            result.append(shifted)
        elif ch.isdigit():
            shifted = str((int(ch) + x) % 10)
            result.append(shifted)
        else:
            result.append(ch)
    return ''.join(result)

def find_rot_ciphers(text):
    found = {}
    rot13_decoded = rot_x(text, 13)
    if rot13_decoded != text:
        found['ROT13'] = rot13_decoded

    digits = re.findall(r'\d', text)
    if digits:
        rot5_decoded = rot_x(text, 5)
        if rot5_decoded != text:
            found['ROT5'] = rot5_decoded

    return found

def analyze_visual(image_path):
    image = preprocess(Image.open(image_path).convert("RGB")).unsqueeze(0).to(device)
    prompts = nsfw_prompts + safe_prompts
    tokens = tokenizer(prompts).to(device)

    with torch.no_grad():
        image_feat = model.encode_image(image)
        text_feat = model.encode_text(tokens)

        image_feat /= image_feat.norm(dim=-1, keepdim=True)
        text_feat /= text_feat.norm(dim=-1, keepdim=True)

        similarity = (100.0 * image_feat @ text_feat.T).softmax(dim=-1).squeeze()

    nsfw_score = float(similarity[:len(nsfw_prompts)].sum()) * 100
    return nsfw_score

def analyze_text(image_path):
    text_blocks = ocr_reader.readtext(image_path, detail=0)
    all_text = " ".join(text_blocks).lower()

    flagged = [kw for kw in flagged_keywords if re.search(rf"\b{re.escape(kw)}\b", all_text)]
    morse_msgs = find_morse_in_text(all_text)
    rot_msgs = find_rot_ciphers(all_text)

    return flagged, morse_msgs, rot_msgs, all_text

def hybrid_analysis(image_path, unsafe_threshold=70, flagged_word_penalty=15):
    nsfw_score = analyze_visual(image_path)
    flagged_words, morse_msgs, rot_msgs, full_text = analyze_text(image_path)

    unsafe_score = nsfw_score + len(flagged_words)*flagged_word_penalty
    unsafe_score = min(100, max(0, unsafe_score))

    is_safe = unsafe_score < unsafe_threshold

    explanation = f"Visual NSFW score: {nsfw_score:.1f}/100 | Text flags: {len(flagged_words)} found"
    if flagged_words:
        explanation += f" ({', '.join(flagged_words)})"

    if morse_msgs:
        explanation += f" | Morse code decoded: {'; '.join(morse_msgs)}"
    if rot_msgs:
        explanation += f" | ROT ciphers decoded: " + "; ".join(f"{k}: {v}" for k, v in rot_msgs.items())

    final_statement = (
        f"Unsafe Rating: {unsafe_score}/100\n"
        f"→ This image {'IS' if is_safe else 'is NOT'} safe for kids.\n"
        f"{explanation}"
    )

    return {
        "image_path": image_path,
        "unsafe_score": unsafe_score,
        "is_safe": is_safe,
        "nsfw_score": nsfw_score,
        "text_flags": flagged_words,
        "morse_decoded": morse_msgs,
        "rot_decoded": rot_msgs,
        "ocr_text": full_text,
        "summary": final_statement
    }
