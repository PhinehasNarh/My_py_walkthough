"""
27 - Resume vs Job-Description ATS Matcher
Project: See how well your resume matches a job description before you apply.

Applicant tracking systems rank resumes by keyword overlap with the job post. This tool
extracts the meaningful words from both, computes a match score, and lists the important
terms from the job description that your resume is missing. Pure standard library.

Usage:
  python main.py resume.txt job.txt
  python main.py resume.txt job.txt --top 25
"""

import argparse
import re
from collections import Counter
from pathlib import Path

# Very common words that carry no signal for matching.
STOPWORDS = set("""
a an and are as at be by for from has have in is it its of on or that the to with
you your we our will work team role job company candidate experience years ability
strong excellent good using use used able including etc this they their them
""".split())

WORD_RE = re.compile(r"[A-Za-z][A-Za-z+#.\-]{1,}")


def keywords(text: str):
    words = [w.lower().strip(".-") for w in WORD_RE.findall(text)]
    return [w for w in words if w and w not in STOPWORDS and len(w) > 2]


def analyze(resume_text: str, job_text: str, top: int):
    resume_set = set(keywords(resume_text))
    job_counts = Counter(keywords(job_text))

    # The job's most-emphasized terms are the ones to match.
    important = [w for w, _ in job_counts.most_common(top)]
    matched = [w for w in important if w in resume_set]
    missing = [w for w in important if w not in resume_set]

    score = round(100 * len(matched) / len(important), 1) if important else 0.0
    return score, matched, missing


def main():
    parser = argparse.ArgumentParser(description="Match a resume against a job description.")
    parser.add_argument("resume", type=Path)
    parser.add_argument("job", type=Path)
    parser.add_argument("--top", type=int, default=20,
                        help="How many top job keywords to score against (default 20).")
    args = parser.parse_args()

    resume_text = args.resume.read_text(encoding="utf-8", errors="ignore")
    job_text = args.job.read_text(encoding="utf-8", errors="ignore")

    score, matched, missing = analyze(resume_text, job_text, args.top)

    print(f"Match score: {score}%  ({len(matched)}/{len(matched) + len(missing)} key terms)\n")
    print("Matched terms:")
    print("  " + (", ".join(matched) if matched else "(none)"))
    print("\nMissing terms to consider adding:")
    print("  " + (", ".join(missing) if missing else "(none)"))


if __name__ == "__main__":
    main()
