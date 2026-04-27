import React from 'react';
import { Table, Tag, Button, Card, Progress, Row, Col } from 'antd';

const RecommendationList = ({ recommendations, onGenerateVolunteerTable }) => {
  const columns = [
    {
      title: '梯度',
      dataIndex: 'level',
      key: 'level',
      render: (level) => {
        const colorMap = {
          '冲': 'red',
          '稳': 'blue',
          '保': 'green'
        };
        return <Tag color={colorMap[level]}>{level}</Tag>;
      }
    },
    {
      title: '院校',
      dataIndex: 'university_name',
      key: 'university'
    },
    {
      title: '专业',
      dataIndex: 'major',
      key: 'major'
    },
    {
      title: '录取概率',
      dataIndex: 'admission_probability',
      key: 'probability',
      render: (prob) => (
        <Progress 
          percent={prob} 
          size="small" 
          status={prob > 70 ? 'success' : prob > 40 ? 'normal' : 'exception'}
        />
      )
    },
    {
      title: '建议排序',
      dataIndex: 'suggested_order',
      key: 'order'
    }
  ];

  const 冲数量 = recommendations.filter(r => r.level === '冲').length;
  const 稳数量 = recommendations.filter(r => r.level === '稳').length;
  const 保数量 = recommendations.filter(r => r.level === '保').length;

  return (
    <div>
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={8}>
          <Card>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: 32, color: '#ff4d4f', fontWeight: 'bold' }}>{冲数量}</div>
              <div>冲刺院校</div>
            </div>
          </Card>
        </Col>
        <Col span={8}>
          <Card>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: 32, color: '#1890ff', fontWeight: 'bold' }}>{稳数量}</div>
              <div>稳妥院校</div>
            </div>
          </Card>
        </Col>
        <Col span={8}>
          <Card>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: 32, color: '#52c41a', fontWeight: 'bold' }}>{保数量}</div>
              <div>保底院校</div>
            </div>
          </Card>
        </Col>
      </Row>

      <Table 
        dataSource={recommendations} 
        columns={columns} 
        rowKey="suggested_order"
        pagination={{ pageSize: 10 }}
      />

      <Button 
        type="primary" 
        size="large" 
        block 
        style={{ marginTop: 24 }}
        onClick={onGenerateVolunteerTable}
      >
        📋 生成志愿方案表
      </Button>
    </div>
  );
};

export default RecommendationList;
