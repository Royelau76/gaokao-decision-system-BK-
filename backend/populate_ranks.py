"""Populate min_rank in yunnan_physics_scores using score-to-rank mapping."""
import sys
sys.path.insert(0, '.')
from db import get_connection

# 2024 Yunnan physics score-to-rank mapping (key points from 一分一段表)
SCORE_RANK_MAP = {
    731: 1,   730: 2,   720: 10,  719: 12,
    710: 32,  703: 56,  702: 62,  700: 76,
    699: 85,  698: 94,  697: 103, 696: 112,
    695: 122, 694: 133, 693: 145, 692: 158,
    690: 172, 689: 187, 688: 203, 687: 220,
    686: 238, 685: 258, 684: 280, 683: 303,
    682: 328, 681: 355, 680: 383, 679: 413,
    678: 445, 677: 479, 676: 515, 675: 553,
    674: 593, 673: 636, 672: 682, 671: 730,
    670: 781, 669: 835, 668: 892, 667: 952,
    666: 1015, 665: 1082, 664: 1153, 663: 1227,
    662: 1306, 661: 1389, 660: 1476, 659: 1568,
    658: 1665, 657: 1767, 656: 1874, 655: 1987,
    654: 2105, 653: 2229, 652: 2359, 651: 2496,
    650: 2640, 649: 2791, 648: 2949, 647: 3115,
    646: 3289, 645: 3471, 644: 3661, 643: 3859,
    642: 4060, 641: 4270, 640: 4490, 639: 4720,
    638: 4960, 637: 5210, 636: 5470, 635: 5740,
    634: 6020, 633: 6310, 632: 6610, 631: 6920,
    630: 7240, 629: 7570, 628: 7910, 627: 8260,
    626: 8620, 625: 8990, 624: 9370, 623: 9760,
    622: 10160, 621: 10570, 620: 10990, 619: 11420,
    618: 11860, 617: 12310, 616: 12770, 615: 13240,
    614: 13720, 613: 14210, 612: 14710, 611: 15220,
    610: 15740,
}


def score_to_rank(score):
    """Estimate rank from score using linear interpolation."""
    scores = sorted(SCORE_RANK_MAP.keys())
    if score >= max(scores):
        return SCORE_RANK_MAP[max(scores)]
    if score <= min(scores):
        return SCORE_RANK_MAP[min(scores)]
    for i in range(len(scores) - 1):
        if scores[i] <= score <= scores[i + 1]:
            x1, y1 = scores[i], SCORE_RANK_MAP[scores[i]]
            x2, y2 = scores[i + 1], SCORE_RANK_MAP[scores[i + 1]]
            return int(y1 + (y2 - y1) * (score - x1) / (x2 - x1))
    return 5000


def main():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, min_score, min_rank FROM yunnan_physics_scores WHERE min_rank IS NULL")
    rows = cursor.fetchall()

    updated = 0
    for row in rows:
        estimated_rank = score_to_rank(row['min_score'])
        cursor.execute(
            "UPDATE yunnan_physics_scores SET min_rank = ? WHERE id = ?",
            (estimated_rank, row['id'])
        )
        updated += 1

    conn.commit()

    # Show distribution
    cursor.execute("""
        SELECT university_name, major_category, min_score, min_rank
        FROM yunnan_physics_scores
        ORDER BY min_rank
        LIMIT 10
    """)
    print(f"Updated {updated} rows. Sample:")
    for r in cursor.fetchall():
        print(f"  {r['university_name']} {r['major_category']}: {r['min_score']}分 -> {r['min_rank']}名")

    conn.close()
    print("Done.")


if __name__ == '__main__':
    main()
