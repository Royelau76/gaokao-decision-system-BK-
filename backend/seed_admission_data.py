"""
Seed realistic admission score data for existing universities.
Based on approximate 2024 Yunnan physics-track admission scores.
"""
import sys
sys.path.insert(0, '.')
from db import get_connection

# University ID → [(major_category, major_code, enrollment_count, max_score, min_score, avg_score)]
# Scores based on publicly available 2024 Yunnan admission data (approximate)
SEED_DATA = {
    'sjtu': [  # 上海交通大学 ~680-695
        ('电子信息类', '0807', 2, 695, 690, 692),
        ('人工智能', '080717', 2, 697, 692, 694),
        ('计算机科学与技术', '080901', 2, 693, 688, 690),
        ('机械类', '0802', 3, 685, 680, 682),
        ('材料科学与工程', '0804', 2, 682, 678, 680),
        ('经济管理试验班', '0201', 2, 688, 683, 685),
        ('理科试验班', '0700', 3, 690, 685, 687),
    ],
    'ustc': [  # 中国科学技术大学 ~680-695
        ('物理学类', '0702', 3, 693, 685, 689),
        ('计算机类', '0809', 2, 690, 683, 686),
        ('数学类', '0701', 2, 688, 682, 685),
        ('化学类', '0703', 2, 684, 678, 681),
        ('电子信息类', '0807', 3, 687, 680, 683),
        ('工科试验班', '0800', 3, 685, 678, 681),
    ],
    'buaa': [  # 北京航空航天大学 ~660-675
        ('航空航天类', '0820', 3, 678, 668, 673),
        ('计算机科学与技术', '080901', 3, 680, 672, 676),
        ('软件工程', '080902', 2, 675, 667, 671),
        ('自动化类', '0808', 3, 672, 663, 667),
        ('电子信息工程', '080701', 2, 674, 665, 669),
        ('机械工程', '0802', 3, 668, 660, 664),
    ],
    'bit': [  # 北京理工大学 ~650-665
        ('计算机科学与技术', '080901', 2, 668, 660, 664),
        ('自动化', '0808', 3, 665, 656, 660),
        ('电子信息工程', '080701', 3, 663, 654, 658),
        ('车辆工程', '080207', 2, 660, 652, 656),
        ('材料科学与工程', '0804', 3, 658, 650, 654),
        ('数学与应用数学', '070101', 2, 662, 654, 658),
    ],
    'hit': [  # 哈尔滨工业大学 ~645-660
        ('计算机科学与技术', '080901', 3, 662, 654, 658),
        ('自动化', '0808', 3, 660, 651, 655),
        ('机械设计制造及其自动化', '080202', 3, 658, 648, 653),
        ('电气工程及其自动化', '080601', 2, 656, 647, 651),
        ('土木工程', '0810', 3, 650, 642, 646),
        ('材料科学与工程', '0804', 2, 653, 645, 649),
    ],
    'xjtu': [  # 西安交通大学 ~640-655
        ('电气工程及其自动化', '080601', 3, 658, 648, 653),
        ('能源与动力工程', '0805', 3, 655, 645, 650),
        ('机械工程', '0802', 3, 653, 643, 648),
        ('计算机科学与技术', '080901', 2, 660, 650, 655),
        ('自动化', '0808', 2, 656, 646, 651),
        ('核工程与核技术', '0822', 2, 648, 640, 644),
    ],
    'uestc': [  # 电子科技大学 ~630-650
        ('电子信息工程', '080701', 3, 652, 642, 647),
        ('通信工程', '080703', 3, 650, 640, 645),
        ('计算机科学与技术', '080901', 3, 655, 645, 650),
        ('微电子科学与工程', '080704', 2, 648, 638, 643),
        ('软件工程', '080902', 3, 647, 637, 642),
        ('自动化', '0808', 2, 645, 635, 640),
    ],
    'nankeda': [  # 南方科技大学 ~620-640 (综合评价为主)
        ('物理学', '070201', 2, 640, 625, 632),
        ('计算机科学与技术', '080901', 2, 642, 628, 635),
        ('生物医学工程', '0826', 2, 635, 620, 627),
        ('材料科学与工程', '0804', 2, 633, 618, 625),
        ('微电子科学与工程', '080704', 2, 638, 623, 630),
        ('数据科学与大数据技术', '080910', 2, 640, 626, 633),
    ],
    'shanghaitech': [  # 上海科技大学 ~615-635 (综合评价)
        ('计算机科学与技术', '080901', 2, 638, 622, 630),
        ('电子信息工程', '080701', 2, 635, 620, 627),
        ('材料科学与工程', '0804', 2, 630, 615, 622),
        ('生物科学', '0710', 2, 628, 613, 620),
        ('物理学', '0702', 2, 632, 618, 625),
    ],
}


def seed():
    conn = get_connection()
    cursor = conn.cursor()

    # Check existing university IDs
    cursor.execute("SELECT id, name FROM universities")
    unis = {row['id']: row['name'] for row in cursor.fetchall()}
    print(f"Universities in DB: {list(unis.keys())}")

    total = 0
    for uid, majors in SEED_DATA.items():
        if uid not in unis:
            print(f"  [SKIP] {uid} - not in universities table")
            continue

        name = unis[uid]
        for major_cat, code, count, max_s, min_s, avg_s in majors:
            try:
                cursor.execute('''
                INSERT OR REPLACE INTO yunnan_physics_scores
                    (university_id, university_name, year, major_category, major_code,
                     enrollment_count, max_score, min_score, avg_score)
                VALUES (?, ?, 2024, ?, ?, ?, ?, ?, ?)
                ''', (uid, name, major_cat, code, count, max_s, min_s, avg_s))
                total += 1
            except Exception as e:
                print(f"  [FAIL] {uid}/{major_cat}: {e}")

    conn.commit()

    # Show summary
    cursor.execute("""
        SELECT university_name, COUNT(*) as majors,
               MIN(min_score) as lowest, MAX(min_score) as highest
        FROM yunnan_physics_scores
        GROUP BY university_id ORDER BY highest DESC
    """)
    print(f"\nSeeded {total} new rows. Current data:")
    for row in cursor.fetchall():
        print(f"  {row['university_name']}: {row['majors']} majors, "
              f"{row['lowest']}-{row['highest']}")

    conn.close()
    print("\nDone.")


if __name__ == '__main__':
    seed()
