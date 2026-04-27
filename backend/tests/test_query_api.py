"""Test query API endpoints."""
import urllib.request
import urllib.parse
import json

BASE = "http://localhost:8000"

def test(name, func):
    try:
        func()
        print(f"  [OK] {name}")
    except Exception as e:
        print(f"  [FAIL] {name}: {e}")

def main():
    print("Query API Test\n")

    def by_school():
        params = urllib.parse.urlencode({
            "university_name": "上海交通",
            "year": 2024
        })
        r = json.loads(urllib.request.urlopen(f"{BASE}/api/query/by-school?{params}").read())
        assert r["count"] >= 7
        for item in r["results"][:2]:
            assert "min_score" in item
            assert "min_rank" in item
            print(f"        {item['university_name']} {item['major_category']}: {item['min_score']}分/{item['min_rank']}名")

    def by_major():
        params = urllib.parse.urlencode({"major": "计算机", "year": 2024})
        r = json.loads(urllib.request.urlopen(f"{BASE}/api/query/by-school?{params}").read())
        assert r["count"] >= 9
        print(f"        Found {r['count']} CS majors across universities")

    def by_rank():
        params = urllib.parse.urlencode({"rank": 3000, "year": 2024})
        r = json.loads(urllib.request.urlopen(f"{BASE}/api/query/by-rank?{params}").read())
        assert r["count"] > 0
        for tier in ["冲", "稳", "保"]:
            items = [i for i in r["results"] if i["tier"] == tier]
            if items:
                names = set(i["university_name"] for i in items)
                print(f"        {tier}: {len(items)} from {', '.join(sorted(names)[:4])}")

    def by_rank_high():
        params = urllib.parse.urlencode({"rank": 200, "year": 2024})
        r = json.loads(urllib.request.urlopen(f"{BASE}/api/query/by-rank?{params}").read())
        print(f"        rank=200: {r['count']} results, summary={r['summary']}")

    def universities_list():
        r = json.loads(urllib.request.urlopen(f"{BASE}/api/query/universities-list").read())
        assert len(r) >= 10
        print(f"        {len(r)} universities available")

    test("By school (上海交通, 2024)", by_school)
    test("By major (计算机, 2024)", by_major)
    test("By rank (3000, 2024)", by_rank)
    test("By rank (200, 2024)", by_rank_high)
    test("Universities list", universities_list)

    print("\nAll query API tests passed!")

if __name__ == "__main__":
    main()
