"""Quick live API smoke test — run against running backend."""
import urllib.request
import json

BASE = "http://localhost:8000"

def test(name, func):
    try:
        func()
        print(f"  [OK] {name}")
    except Exception as e:
        print(f"  [FAIL] {name}: {e}")

def main():
    print("API Smoke Test\n")

    def root():
        r = json.loads(urllib.request.urlopen(f"{BASE}/").read())
        assert r["version"] == "1.0.0"

    def universities():
        r = json.loads(urllib.request.urlopen(f"{BASE}/api/universities").read())
        assert len(r) >= 10

    def universities_filter():
        r = json.loads(urllib.request.urlopen(f"{BASE}/api/universities?level=985").read())
        assert all(u["level"] == "985" for u in r)

    def score_conversion():
        r = json.loads(urllib.request.urlopen(f"{BASE}/api/score-conversion?score=650").read())
        assert r["score"] == 650
        assert r["estimated_rank"] > 0

    def recommendations_650():
        body = json.dumps({
            "score": 650, "rank": 876,
            "subjects": ["physics", "chemistry", "biology"],
            "preference_region": ["Shanghai", "Beijing"],
            "preference_major": ["CS", "AI"],
            "risk_tolerance": "稳健"
        }).encode()
        req = urllib.request.Request(f"{BASE}/api/recommendations", data=body,
                                     headers={"Content-Type": "application/json"})
        data = json.loads(urllib.request.urlopen(req).read())
        recs = data["recommendations"]
        assert len(recs) > 0
        s = data["summary"]
        assert s["冲"] + s["稳"] + s["保"] == len(recs)
        # Print tiers
        for level in ["冲", "稳", "保"]:
            items = [r for r in recs if r["level"] == level]
            names = set(r["university_name"] for r in items)
            print(f"        {level}: {len(items)} items from {', '.join(sorted(names)[:3])}")

    def recommendations_620():
        body = json.dumps({
            "score": 620, "rank": 5000,
            "subjects": ["physics"], "preference_region": [],
            "preference_major": [], "risk_tolerance": "保守"
        }).encode()
        req = urllib.request.Request(f"{BASE}/api/recommendations", data=body,
                                     headers={"Content-Type": "application/json"})
        data = json.loads(urllib.request.urlopen(req).read())
        recs = data["recommendations"]
        bao = [r for r in recs if r["level"] == "保"]
        assert len(bao) > 0

    def yunnan_scores():
        r = json.loads(urllib.request.urlopen(f"{BASE}/api/yunnan/scores?year=2024").read())
        assert len(r) >= 50

    def yunnan_scores_filter():
        r = json.loads(urllib.request.urlopen(f"{BASE}/api/yunnan/scores?university_id=beida").read())
        assert all(row["university_id"] == "beida" for row in r)

    def b_segment():
        r = json.loads(urllib.request.urlopen(f"{BASE}/api/yunnan/b-segment/plans/2025/beida").read())
        assert len(r) >= 7

    test("Root", root)
    test("Universities (>=10)", universities)
    test("Universities filter (985)", universities_filter)
    test("Score conversion", score_conversion)
    test("Recommendations (score=650)", recommendations_650)
    test("Recommendations (score=620)", recommendations_620)
    test("Yunnan scores (>=50)", yunnan_scores)
    test("Yunnan scores filter", yunnan_scores_filter)
    test("B-segment plans", b_segment)

    print("\nAll smoke tests passed!")

if __name__ == "__main__":
    main()
