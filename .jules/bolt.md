## 2024-06-06 - [Regex vs Generator Expression for Text Matching]
**Learning:** `re.compile` followed by `search` is over 10x faster than `any(ord(ch) in range for ch in text)` for finding character classes in large strings, because regex search runs entirely in C, while the generator expression yields and evaluates Python objects for every character up to the match.
**Action:** Replace `any(...)` character matching with compiled regexes in hot paths.

## 2026-06-08 - [Cold Path vs Hot Path Optimization]
**Learning:** Optimizing code that only executes during fallback/exception handling (cold path) yields no measurable performance impact. We must target hot paths (like message masking which runs on every single output) for optimizations to be worthwhile.
**Action:** When looking for performance improvements, ensure the target code runs frequently enough to make a difference before optimizing it.

## 2026-06-13 - [Pre-computing regex conditions in hot paths]
**Learning:** Evaluating regex on static config keys in a hot path causes significant overhead. By pre-computing and caching the matched keys at initialization, the hot path avoids redundant regex searches, improving execution time.
**Action:** Identify static conditions evaluated with regex inside hot paths and cache their results during initialization.
