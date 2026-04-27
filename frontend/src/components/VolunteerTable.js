import React from 'react';
import { Table, Tag, Card } from 'antd';

const VolunteerTable = ({ studentInfo, recommendations }) => {
  const dataSource = recommendations.map((rec, index) => ({
    key: index,
    order: index + 1,
    level: rec.level,
    university: rec.university_name,
    major: rec.major,
    probability: rec.admission_probability,
    reason: generateReason(rec)
  }));

  const columns = [
    {
      title: '志愿序号',
      dataIndex: 'order',
      key: 'order',
      width: 100
    },
    {
      title: '梯度',
      dataIndex: 'level',
      key: 'level',
      render: (level) => {
        const colors = { '冲': 'red', '稳': 'blue', '保': 'green' };
        return <Tag color={colors[level]}>{level}</Tag>;
      },
      width: 100
    },
    {
      title: '院校名称',
      dataIndex: 'university',
      key: 'university'
    },
    {
      title: '专业',
      dataIndex: 'major',
      key: 'major'
    },
    {
      title: '录取概率',
      dataIndex: 'probability',
      key: 'probability',
      render: (prob) => `${prob}%`,
      width: 120
    },
    {
      title: '推荐理由',
      dataIndex: 'reason',
      key: 'reason'
    }
  ];

  function generateReason(rec) {
    if (rec.level === '冲') {
      return '位次略优于考生，有一定挑战，但可尝试';
    } else if (rec.level === '稳') {
      return '位次与考生匹配度较高，录取概率大';
    } else {
      return '位次低于考生，作为保底选择';
    }
  }

  return (
    <div>
      <Card title="📋 2026年云南省高考志愿方案表" style={{ marginBottom: 24 }}>
        <p><strong>考生信息：</strong></p>
        <p>分数：{studentInfo?.score} 分 | 位次：约 {studentInfo?.rank} 名</p>
        <p>选科：{studentInfo?.subjects?.join('、')}</p>
        <p>风险偏好：{studentInfo?.risk_tolerance}</p>
      </Card>

      <Table 
        dataSource={dataSource} 
        columns={columns}
        pagination={false}
        bordered
        summary={() => (
          <Table.Summary.Row>
            <Table.Summary.Cell colSpan={6}>
              <div style={{ textAlign: 'center', padding: '10px' }}>
                💡 建议：冲{dataSource.filter(d => d.level === '冲').length}个 + 
                稳{dataSource.filter(d => d.level === '稳').length}个 + 
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
