# GUIDANCE — muscle_text_transform

## When to Use

- Normalise text files before processing (upper/lower/strip)
- Find-replace in config or template files
- Quick word count of a document

## How to Call

```bash
python registry/muscle_text_transform.py --input in.txt --output out.txt --operation upper
python registry/muscle_text_transform.py --input in.txt --output out.txt --operation replace --find "old" --replace "new"
python registry/muscle_text_transform.py --input in.txt --output in.txt --operation word_count
```

### Via Telegram
```
/ticket convert file.txt to uppercase
/ticket replace "foo" with "bar" in config.txt
/ticket count words in document.txt
```
