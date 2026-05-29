import React from 'react';
import { Table, Tag, Card, Tooltip } from 'antd';

const VolunteerTable = ({ studentInfo, recommendations }) => {
  const dataSource = recommendations.map((rec, index) => ({
    key: index,
    order: index + 1,
    level: rec.level,
    university: rec.university_name,
    major: rec.major,
    probability: rec.admission_probability,
    composite: rec.composite_score,
    employment: rec.employment,
    reason: rec.reason || fallbackReason(rec),
  }));

  const columns = [
    { title: '志愿序号', dataIndex: 'order', key: 'order', width: 80 },
    {
      title: '梯度',
      dataIndex: 'level',
      key: 'level',
      width: 70,
      render: (level) => {
        const colors = { '冲': 'red', '稳': 'blue', '保': 'green' };
        return <Tag color={colors[level]}>{level}</Tag>;
      },
    },
    { title: '院校名称', dataIndex: 'university', key: 'university', width: 160 },
    { title: '专业', dataIndex: 'major', key: 'major', width: 200 },
    {
      title: '录取概率',
      dataIndex: 'probability',
      key: 'probability',
      width: 90,
      render: (prob) => `${prob}%`,
    },
    {
      title: '综合评分',
      dataIndex: 'composite',
      key: 'composite',
      width: 90,
      render: (s) => s != null ? <span style={{ fontWeight: 600 }}>{s.toFixed(1)}</span> : '—',
    },
    {
      title: '就业',
      dataIndex: 'employment',
      key: 'employment',
      width: 160,
      render: (emp) => {
        if (!emp) return <span style={{ color: '#B4B4B0' }}>—</span>;
        const parts = [];
        if (emp.employment_rate != null) parts.push(`就业${emp.employment_rate}%`);
        if (emp.salary_range) parts.push(emp.salary_range);
        return parts.join(' / ') || '—';
      },
    },
    {
      title: '推荐理由',
      dataIndex: 'reason',
      key: 'reason',
      render: (text) => (
        <Tooltip title={text}>
          <div style={{
            whiteSpace: 'nowrap',
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            maxWidth: 360,
          }}>{text}</div>
        </Tooltip>
      ),
    },
  ];

  function fallbackReason(rec) {
    if (rec.level === '冲') return '位次略优于考生，有一定挑战';
    if (rec.level === '稳') return '位次与考生匹配度较高';
    return '位次低于考生，作为保底';
  }

  return (
    <div>
      <Card title="2026年云南省高考志愿方案表" style={{ marginBottom: 24 }}>
        <p><strong>考生信息：</strong></p>
        <p>分数：{studentInfo?.score} 分 | 位次：约 {studentInfo?.rank?.toLocaleString()} 名</p>
        <p>选科：{studentInfo?.subjects?.join('、')}</p>
        <p>风险偏好：{studentInfo?.risk_tolerance}</p>
        {studentInfo?.preference_major?.length > 0 && (
          <p>偏好大类：{studentInfo.preference_major.join('、')}</p>
        )}
        {studentInfo?.preference_region?.length > 0 && (
          <p>偏好地区：{studentInfo.preference_region.join('、')}</p>
        )}
      </Card>

      <Table
        dataSource={dataSource}
        columns={columns}
        pagination={false}
        bordered
        scroll={{ x: 1100 }}
        summary={() => (
          <Table.Summary.Row>
            <Table.Summary.Cell colSpan={9}>
              <div style={{ textAlign: 'center', padding: '10px' }}>
                建议：冲{dataSource.filter(d => d.level === '冲').length}个 ·
                稳{dataSource.filter(d => d.level === '稳').length}个 ·
                保{dataSource.filter(d => d.level === '保').length}个
              </div>
            </Table.Summary.Cell>
          </Table.Summary.Row>
        )}
      />
    </div>
  );
};

export default VolunteerTable;
