#!/usr/bin/env python3
"""
批量导入院校数据工具
支持从CSV、Excel或交互式输入添加院校数据
"""

import sqlite3
import json
import os
import sys

def get_db_path():
    """获取数据库路径"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, '..', '..', 'data')
    return os.path.join(data_dir, 'gaokao.db')

def add_university_interactive():
    """交互式添加单个院校"""
    print("\n📝 交互式添加院校\n")

    uni = {}

    # 基本信息
    uni['id'] = input("院校ID（英文缩写，如 pku）: ").strip()
    uni['name'] = input("院校全称: ").strip()
    uni['province'] = input("省份: ").strip()
    uni['city'] = input("城市: ").strip()

    # 层次
    print("\n层次选择: 1-985  2-211  3-双一流  4-普通本科")
    level_map = {'1': '985', '2': '211', '3': '双一流', '4': '普通本科'}
    level_choice = input("请选择 (1-4): ").strip()
    uni['level'] = level_map.get(level_choice, '普通本科')

    # 招生方式
    print("\n招生方式: 1-统招  2-强基计划  3-综合评价  4-强基/统招")
    mode_map = {'1': '统招', '2': '强基计划', '3': '综合评价', '4': '强基/统招'}
    mode_choice = input("请选择 (1-4): ").strip()
    uni['admission_mode'] = mode_map.get(mode_choice, '统招')

    uni['website'] = input("官网地址（可选）: ").strip()

    # 录取数据
    uni['min_score_2025'] = int(input("\n2025年最低分: "))
    uni['min_rank_2025'] = int(input("2025年最低位次: "))

    # 选科要求
    print("\n选科要求（多个用逗号分隔，如: 物理,化学）")
    subjects_input = input("选科: ").strip()
    uni['subjects_required'] = [s.strip() for s in subjects_input.split(',') if s.strip()]

    # 专业
    print("\n添加专业（至少1个）")
    majors = []
    while True:
        major_name = input(f"  专业{len(majors)+1}名称（留空结束）: ").strip()
        if not major_name:
            break
        major_code = input(f"  专业代码: ").strip()
        major_eval = input(f"  学科评估（如A+/A/B+或'快速发展中'）: ").strip()
        majors.append({
            'name': major_name,
            'code': major_code,
            'evaluation': major_eval
        })
    uni['majors'] = majors

    # 优劣势
    print("\n优势（多个用逗号分隔，可选）")
    adv_input = input("优势: ").strip()
    uni['advantages'] = [a.strip() for a in adv_input.split(',') if a.strip()]

    print("\n劣势（多个用逗号分隔，可选）")
    dis_input = input("劣势: ").strip()
    uni['disadvantages'] = [d.strip() for d in dis_input.split(',') if d.strip()]

    return uni

def add_university_to_db(uni):
    """将院校添加到数据库"""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        cursor.execute('''
        INSERT INTO universities (
            id, name, province, city, level, admission_mode, website,
            min_score_2025, min_rank_2025, subjects_required, majors,
            advantages, disadvantages
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            uni['id'],
            uni['name'],
            uni.get('province', ''),
            uni.get('city', ''),
            uni.get('level', ''),
            uni.get('admission_mode', ''),
            uni.get('website', ''),
            uni.get('min_score_2025', 0),
            uni.get('min_rank_2025', 0),
            json.dumps(uni.get('subjects_required', []), ensure_ascii=False),
            json.dumps(uni.get('majors', []), ensure_ascii=False),
            json.dumps(uni.get('advantages', []), ensure_ascii=False),
            json.dumps(uni.get('disadvantages', []), ensure_ascii=False)
        ))
        conn.commit()
        print(f"✅ {uni['name']} 添加成功！")
        return True
    except sqlite3.IntegrityError:
        print(f"❌ 错误：院校ID '{uni['id']}' 已存在")
        return False
    except Exception as e:
        print(f"❌ 添加失败：{e}")
        return False
    finally:
        conn.close()

def batch_add_from_template():
    """从模板批量添加"""
    print("\n📋 批量添加模板")
    print("请准备一个包含多所院校的JSON文件")
    print("格式参考: data/universities.json\n")

    file_path = input("JSON文件路径: ").strip()

    if not os.path.exists(file_path):
        print(f"❌ 文件不存在: {file_path}")
        return

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            universities = json.load(f)

        success_count = 0
        for uni in universities:
            if add_university_to_db(uni):
                success_count += 1

        print(f"\n✅ 成功添加 {success_count}/{len(universities)} 所院校")
    except Exception as e:
        print(f"❌ 读取文件失败: {e}")

def list_universities():
    """列出所有院校"""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM universities ORDER BY min_rank_2025')
    rows = cursor.fetchall()

    print(f"\n📊 当前数据库中共有 {len(rows)} 所院校\n")
    print(f"{'ID':<15} {'院校名称':<20} {'层次':<8} {'2025最低分':<10} {'位次':<8}")
    print("-" * 70)

    for row in rows:
        print(f"{row['id']:<15} {row['name']:<18} {row['level']:<8} "
              f"{row['min_score_2025']:<10} {row['min_rank_2025']:<8}")

    conn.close()

def delete_university():
    """删除院校"""
    uni_id = input("\n请输入要删除的院校ID: ").strip()

    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('DELETE FROM universities WHERE id = ?', (uni_id,))

    if cursor.rowcount > 0:
        conn.commit()
        print(f"✅ 已删除院校: {uni_id}")
    else:
        print(f"❌ 未找到院校: {uni_id}")

    conn.close()

def export_to_json():
    """导出到JSON"""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM universities')
    rows = cursor.fetchall()

    universities = []
    for row in rows:
        uni = dict(row)
        # 解析JSON字段
        uni['subjects_required'] = json.loads(uni['subjects_required']) if uni['subjects_required'] else []
        uni['majors'] = json.loads(uni['majors']) if uni['majors'] else []
        uni['advantages'] = json.loads(uni['advantages']) if uni['advantages'] else []
        uni['disadvantages'] = json.loads(uni['disadvantages']) if uni['disadvantages'] else []
        universities.append(uni)

    conn.close()

    output_file = input("\n输出文件名（默认: universities_export.json）: ").strip()
    if not output_file:
        output_file = "universities_export.json"

    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(script_dir, '..', '..', 'data', output_file)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(universities, f, ensure_ascii=False, indent=2)

    print(f"✅ 已导出到: {output_path}")

def quick_add_common_universities():
    """快速添加常见院校（预设数据）"""
    print("\n🚀 快速添加常见985/211院校")
    print("这将添加一些常见的高校数据（需要你提供2025年云南录取数据）\n")

    common_unis = [
        {"id": "pku", "name": "北京大学", "province": "北京", "level": "985"},
        {"id": "thu", "name": "清华大学", "province": "北京", "level": "985"},
        {"id": "zju", "name": "浙江大学", "province": "浙江", "level": "985"},
        {"id": "nju", "name": "南京大学", "province": "江苏", "level": "985"},
        {"id": "fdu", "name": "复旦大学", "province": "上海", "level": "985"},
    ]

    print("可添加的院校:")
    for i, uni in enumerate(common_unis, 1):
        print(f"{i}. {uni['name']}")

    choice = input("\n选择要添加的院校编号（多个用逗号分隔，0=全部）: ").strip()

    if choice == '0':
        selected = common_unis
    else:
        indices = [int(x.strip())-1 for x in choice.split(',') if x.strip().isdigit()]
        selected = [common_unis[i] for i in indices if 0 <= i < len(common_unis)]

    for uni in selected:
        print(f"\n--- 添加 {uni['name']} ---")
        uni['city'] = input(f"城市（默认: {uni['province']}）: ").strip() or uni['province']
        uni['admission_mode'] = input("招生方式（统招/强基/综合评价）: ").strip() or "统招"
        uni['min_score_2025'] = int(input("2025年最低分: "))
        uni['min_rank_2025'] = int(input("2025年最低位次: "))

        subjects = input("选科要求（如: 物理,化学）: ").strip()
        uni['subjects_required'] = [s.strip() for s in subjects.split(',')]

        # 简化专业输入
        uni['majors'] = [
            {"name": "计算机科学与技术", "code": "080901", "evaluation": "A+"},
            {"name": "软件工程", "code": "080902", "evaluation": "A+"}
        ]
        uni['advantages'] = ["顶尖名校", "就业前景好"]
        uni['disadvantages'] = ["录取分数极高"]
        uni['website'] = ""

        add_university_to_db(uni)

def main():
    """主菜单"""
    while True:
        print("\n" + "="*50)
        print("🎓 云志选 - 院校数据管理工具")
        print("="*50)
        print("1. 交互式添加单个院校")
        print("2. 从JSON文件批量导入")
        print("3. 快速添加常见985/211院校")
        print("4. 查看所有院校")
        print("5. 删除院校")
        print("6. 导出到JSON")
        print("0. 退出")
        print("="*50)

        choice = input("\n请选择操作 (0-6): ").strip()

        if choice == '1':
            uni = add_university_interactive()
            add_university_to_db(uni)
        elif choice == '2':
            batch_add_from_template()
        elif choice == '3':
            quick_add_common_universities()
        elif choice == '4':
            list_universities()
        elif choice == '5':
            delete_university()
        elif choice == '6':
            export_to_json()
        elif choice == '0':
            print("\n👋 再见！")
            break
        else:
            print("❌ 无效选择，请重试")

if __name__ == "__main__":
    main()
