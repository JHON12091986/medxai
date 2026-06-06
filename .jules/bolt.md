## 2024-06-06 - [Regex vs Generator Expression for Text Matching]
**Learning:** `re.compile` followed by `search` is over 10x faster than `any(ord(ch) in range for ch in text)` for finding character classes in large strings, because regex search runs entirely in C, while the generator expression yields and evaluates Python objects for every character up to the match.
**Action:** Replace `any(...)` character matching with compiled regexes in hot paths.
