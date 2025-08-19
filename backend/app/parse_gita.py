
# backend/app/parse_gita.py
import re
from pdfminer.high_level import extract_text
from sqlalchemy.orm import Session
from . import models, database


PDF_PATH = "../Bhagavad-gita-As-It-Is.pdf"

def extract_slokams():
    text = extract_text(PDF_PATH)
    text = re.sub(r'\r', '', text)

    text_pat = re.compile(r'\nTEXTS?\s+(\d+(?:\s*-\s*\d+)?)')
    segments = list(text_pat.finditer(text))

    slokams = []
    current_chapter = 1
    chapter_finder = re.compile(r'\nCHAPTER\s+([A-Z]+)', re.IGNORECASE)
    word_to_num = {
        'ONE':1,'TWO':2,'THREE':3,'FOUR':4,'FIVE':5,'SIX':6,'SEVEN':7,'EIGHT':8,
        'NINE':9,'TEN':10,'ELEVEN':11,'TWELVE':12,'THIRTEEN':13,'FOURTEEN':14,
        'FIFTEEN':15,'SIXTEEN':16,'SEVENTEEN':17,'EIGHTEEN':18
    }

    def number_range(s):
        if '-' in s:
            a,b = re.split(r'\s*-\s*', s)
            return list(range(int(a), int(b)+1))
        return [int(s)]

    for i, m in enumerate(segments):
        start = m.start()
        end = segments[i+1].start() if i+1 < len(segments) else len(text)
        block = text[start:end]

        chap_match = chapter_finder.search(block)
        if chap_match:
            current_chapter = word_to_num.get(chap_match.group(1).upper(), current_chapter)

        nums = number_range(m.group(1))

        trans_match = re.search(r'TRANSLATION(.*?)(PURPORT|TEXTS?\s+\d+|\nCHAPTER|$)', block, re.DOTALL)
        translation = trans_match.group(1).strip() if trans_match else ""

        pur_match = re.search(r'PURPORT(.*?)(TEXTS?\s+\d+|\nCHAPTER|$)', block, re.DOTALL)
        purport = pur_match.group(1).strip() if pur_match else ""

        verse_text = block[m.end(): trans_match.start() if trans_match else len(block)].strip()

        def first_sentences(text, n=2):
            parts = re.split(r'(?<=[.!?])\s+', text.strip())
            return " ".join(parts[:n])
        bhavam = first_sentences(purport if purport else translation, 2)

        for v in nums:
            slokams.append(models.Slokam(
                chapter=current_chapter,
                verse=v,
                verse_text=verse_text,
                translation=translation,
                purport=purport,
                bhavam=bhavam
            ))
    return slokams

def main():
    models.Base.metadata.create_all(bind=database.engine)  # ensure table exists
    db: Session = database.SessionLocal()

    slokams = extract_slokams()
    db.add_all(slokams)
    db.commit()
    print(f"Inserted {len(slokams)} slokams into DB")

if __name__ == "__main__":
    main()
