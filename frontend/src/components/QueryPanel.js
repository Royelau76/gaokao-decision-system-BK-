import React, { useState, useEffect } from 'react';
import { Tabs, Table, Tag, Input, Select, Button, Card, Row, Col, message, Empty } from 'antd';
import { SearchOutlined } from '@ant-design/icons';

const QueryPanel = () => {
  const [universities, setUniversities] = useState([]);

  useEffect(() => {
    fetch('/api/query/universities-list')
      .then(r => r.json())
      .then(data => setUniversities(data))
      .catch(() => {});
  }, []);

  const tabItems = [
    {
      key: 'school',
      label: '按院校专业查询',
      children: <SchoolQuery universities={universities} />
    },
    {
      key: 'rank',
      label: '按位次查询',
      children: <RankQuery />
    },
    {
      key: 'plan',
      label: '按招生计划查询',
      children: <PlanQuery universities={universities} />
    }
  ];

  return (
    <Card title="数据查询" style={{ marginBottom: 24 }}>
      <Tabs items={tabItems} />
    </Card>
  );
};

// ====== Tab 1: 按院校专业查询 ======
function SchoolQuery({ universities }) {
  const [uniName, setUniName] = useState(undefined);
  const [major, setMajor] = useState('');
  const [year, setYear] = useState(2024);
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSearch = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (uniName) params.append('university_name', uniName);
      if (major) params.append('major', major);
      params.append('year', year);
      params.append('limit', '100');

      const resp = await fetch(`/api/query/by-school?${params}`);
      const data = await resp.json();
      setResults(data);
    } catch (e) {
      message.error('查询失败');
    }
    setLoading(false);
  };

  const columns = [
    { title: '院校', dataIndex: 'university_name', key: 'name', width: 160 },
    {
      title: '层次', dataIndex: 'level', key: 'level', width: 70,
      render: (v) => <Tag color={v === '985' ? 'gold' : v === '211' ? 'blue' : 'default'}>{v}</Tag>
    },
    { title: '专业', dataIndex: 'major_category', key: 'major', width: 130 },
    { title: '年份', dataIndex: 'year', key: 'year', width: 70 },
    { title: '最低分', dataIndex: 'min_score', key: 'score', width: 80 },
    { title: '最高分', dataIndex: 'max_score', key: 'max', width: 80 },
    { title: '平均分', dataIndex: 'avg_score', key: 'avg', width: 80 },
    { title: '最低位次', dataIndex: 'min_rank', key: 'rank', width: 90 },
    { title: '招生人数', dataIndex: 'enrollment_count', key: 'count', width: 80 },
    { title: '省份', dataIndex: 'province', key: 'province', width: 70 },
  ];

  return (
    <div>
      <Row gutter={12} style={{ marginBottom: 16 }}>
        <Col span={6}>
          <Select
            showSearch
            allowClear
            placeholder="选择院校"
            value={uniName}
            onChange={setUniName}
            style={{ width: '100%' }}
            filterOption={(input, option) =>
              option.children.toLowerCase().includes(input.toLowerCase())
            }
          >
            {universities.map(u => (
              <Select.Option key={u.university_id} value={u.university_name}>
                {u.university_name}
              </Select.Option>
            ))}
          </Select>
        </Col>
        <Col span={5}>
          <Input
            placeholder="专业（如：计算机）"
            value={major}
            onChange={e => setMajor(e.target.value)}
            allowClear
          />
        </Col>
        <Col span={4}>
          <Select value={year} onChange={setYear} style={{ width: '100%' }}>
            <Select.Option value={2024}>2024年</Select.Option>
            <Select.Option value={2025}>2025年</Select.Option>
          </Select>
        </Col>
        <Col span={3}>
          <Button type="primary" icon={<SearchOutlined />} onClick={handleSearch} loading={loading}>
            查询
          </Button>
        </Col>
      </Row>

      {results && (
        <div>
          <p style={{ color: '#888' }}>找到 {results.count} 条记录</p>
          <Table
            dataSource={results.results}
            columns={columns}
            rowKey={(r, i) => `${r.university_id}-${r.major_category}-${i}`}
            size="small"
            pagination={{ pageSize: 15 }}
            scroll={{ x: 900 }}
          />
        </div>
      )}
      {!results && <Empty description="输入条件后点击查询" />}
    </div>
  );
}

// ====== Tab 2: 按位次查询 ======
function RankQuery() {
  const [rank, setRank] = useState('');
  const [year, setYear] = useState(2024);
  const [tolerance, setTolerance] = useState(500);
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSearch = async () => {
    if (!rank) return;
    setLoading(true);
    try {
      const params = new URLSearchParams({ rank, year, tolerance, limit: '100' });
      const resp = await fetch(`/api/query/by-rank?${params}`);
      const data = await resp.json();
      setResults(data);
    } catch (e) {
      message.error('查询失败');
    }
    setLoading(false);
  };

  const columns = [
    {
      title: '梯度', dataIndex: 'tier', key: 'tier', width: 70,
      render: (v) => {
        const colors = { '冲': 'red', '稳': 'blue', '保': 'green' };
        return <Tag color={colors[v]}>{v}</Tag>;
      }
    },
    { title: '院校', dataIndex: 'university_name', key: 'name', width: 160 },
    {
      title: '层次', dataIndex: 'level', key: 'level', width: 70,
      render: (v) => <Tag color={v === '985' ? 'gold' : v === '211' ? 'blue' : 'default'}>{v}</Tag>
    },
    { title: '专业', dataIndex: 'major_category', key: 'major', width: 130 },
    { title: '年份', dataIndex: 'year', key: 'year', width: 70 },
    { title: '最低分', dataIndex: 'min_score', key: 'score', width: 80 },
    { title: '最低位次', dataIndex: 'min_rank', key: 'rank', width: 90 },
    { title: '招生人数', dataIndex: 'enrollment_count', key: 'count', width: 80 },
  ];

  return (
    <div>
      <Row gutter={12} style={{ marginBottom: 16 }}>
        <Col span={5}>
          <Input
            placeholder="输入位次（如：3000）"
            value={rank}
            onChange={e => setRank(e.target.value)}
            type="number"
          />
        </Col>
        <Col span={4}>
          <Select value={year} onChange={setYear} style={{ width: '100%' }}>
            <Select.Option value={2024}>2024年</Select.Option>
            <Select.Option value={2025}>2025年</Select.Option>
          </Select>
        </Col>
        <Col span={6}>
          <Select value={tolerance} onChange={setTolerance} style={{ width: '100%' }}>
            <Select.Option value={200}>范围: +/- 200 名</Select.Option>
            <Select.Option value={500}>范围: +/- 500 名</Select.Option>
            <Select.Option value={1000}>范围: +/- 1000 名</Select.Option>
            <Select.Option value={2000}>范围: +/- 2000 名</Select.Option>
          </Select>
        </Col>
        <Col span={3}>
          <Button type="primary" icon={<SearchOutlined />} onClick={handleSearch} loading={loading}>
            查询
          </Button>
        </Col>
      </Row>

      {results && (
        <div>
          <Row gutter={16} style={{ marginBottom: 16 }}>
            <Col span={8}>
              <Card size="small" style={{ background: '#fff2f0' }}>
                <div style={{ textAlign: 'center' }}>
                  <div style={{ fontSize: 28, color: '#ff4d4f', fontWeight: 'bold' }}>{results.summary['冲']}</div>
                  <div>冲刺</div>
                </div>
              </Card>
            </Col>
            <Col span={8}>
              <Card size="small" style={{ background: '#e6f7ff' }}>
                <div style={{ textAlign: 'center' }}>
                  <div style={{ fontSize: 28, color: '#1890ff', fontWeight: 'bold' }}>{results.summary['稳']}</div>
                  <div>稳妥</div>
                </div>
              </Card>
            </Col>
            <Col span={8}>
              <Card size="small" style={{ background: '#f6ffed' }}>
                <div style={{ textAlign: 'center' }}>
                  <div style={{ fontSize: 28, color: '#52c41a', fontWeight: 'bold' }}>{results.summary['保']}</div>
                  <div>保底</div>
                </div>
              </Card>
            </Col>
          </Row>

          <p style={{ color: '#888' }}>
            位次 {results.query.rank} 在 {results.query.year} 年可选 {results.count} 个院校专业
            （范围 +/- {results.query.tolerance} 名）
          </p>
          <Table
            dataSource={results.results}
            columns={columns}
            rowKey={(r, i) => `${r.university_id}-${r.major_category}-${i}`}
            size="small"
            pagination={{ pageSize: 15 }}
            scroll={{ x: 700 }}
          />
        </div>
      )}
      {!results && <Empty description="输入位次后点击查询" />}
    </div>
  );
};

// ====== Tab 3: 按招生计划查询 ======
function PlanQuery({ universities }) {
  const [uniName, setUniName] = useState(undefined);
  const [year, setYear] = useState(2025);
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSearch = async () => {
    if (!uniName) return;
    setLoading(true);
    try {
      const params = new URLSearchParams();
      params.append('university_name', uniName);
      params.append('year', year);
      params.append('limit', '200');

      const resp = await fetch(`/api/query/by-plan?${params}`);
      const data = await resp.json();
      setResults(data);
    } catch (e) {
      message.error('查询失败');
    }
    setLoading(false);
  };

  const columns = [
    { title: '院校', dataIndex: 'university_name', width: 160 },
    { title: '年份', dataIndex: 'year', width: 70 },
    { title: '专业代号', dataIndex: 'major_code', width: 90 },
    { title: '专业组', dataIndex: 'major_group_sequence', width: 80 },
    { title: '专业大类', dataIndex: 'major_category', width: 140 },
    { title: '选考科目', dataIndex: 'required_subjects', width: 90 },
    { title: '招生人数', dataIndex: 'enrollment_count', width: 90 },
    { title: '学费', dataIndex: 'tuition', width: 80 },
    { title: '校区', dataIndex: 'campus', width: 80 },
    {
      title: '包含专业', dataIndex: 'included_majors', width: 200, ellipsis: true,
      render: (v) => {
        if (!v) return '';
        try { return JSON.parse(v).join('、'); } catch { return v; }
      }
    },
  ];

  const totalEnrollment = results
    ? results.results.reduce((sum, r) => sum + (r.enrollment_count || 0), 0)
    : 0;

  return (
    <div>
      <Row gutter={12} style={{ marginBottom: 16 }}>
        <Col span={8}>
          <Select
            showSearch
            allowClear
            placeholder="选择院校"
            value={uniName}
            onChange={setUniName}
            style={{ width: '100%' }}
            filterOption={(input, option) =>
              option.children.toLowerCase().includes(input.toLowerCase())
            }
          >
            {universities.map(u => (
              <Select.Option key={u.university_id} value={u.university_name}>
                {u.university_name}
              </Select.Option>
            ))}
          </Select>
        </Col>
        <Col span={4}>
          <Select value={year} onChange={setYear} style={{ width: '100%' }}>
            <Select.Option value={2024}>2024年</Select.Option>
            <Select.Option value={2025}>2025年</Select.Option>
            <Select.Option value={2026}>2026年</Select.Option>
          </Select>
        </Col>
        <Col span={3}>
          <Button type="primary" icon={<SearchOutlined />} onClick={handleSearch} loading={loading}>
            查询
          </Button>
        </Col>
      </Row>

      {results && (
        <div>
          <p style={{ color: '#888' }}>
            找到 {results.count} 条记录，总招生人数 {totalEnrollment} 人
          </p>
          <Table
            dataSource={results.results}
            columns={columns}
            rowKey={(r, i) => `${r.university_id}-${r.major_code}-${i}`}
            size="small"
            pagination={{ pageSize: 20 }}
            scroll={{ x: 1100 }}
          />
        </div>
      )}
      {!results && <Empty description="选择院校后点击查询" />}
    </div>
  );
}

export default QueryPanel;
