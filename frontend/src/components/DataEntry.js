import React, { useState, useEffect, useCallback } from 'react';
import { Tabs, Table, Tag, Input, Select, Button, Card, Row, Col, message, Modal, Form, Popconfirm, Upload, Space } from 'antd';
import { PlusOutlined, DeleteOutlined, UploadOutlined, DownloadOutlined } from '@ant-design/icons';

const API = '/api/data-entry';

const DataEntry = () => {
  const [universities, setUniversities] = useState([]);

  useEffect(() => {
    fetch(`${API}/universities-list`)
      .then(r => r.json())
      .then(setUniversities)
      .catch(() => {});
  }, []);

  const tabItems = [
    { key: 'scores', label: '录取分数', children: <ScoreEntry universities={universities} /> },
    { key: 'segments', label: '一分一段', children: <SegmentEntry /> },
    { key: 'plans', label: '招生计划', children: <BPlanEntry universities={universities} /> },
    { key: 'universities', label: '院校管理', children: <UniversityEntry /> },
  ];

  return (
    <Card title="数据录入" style={{ maxWidth: 1200, margin: '0 auto' }}>
      <Tabs items={tabItems} />
    </Card>
  );
};

// ======================== 录取分数录入 ========================
function ScoreEntry({ universities }) {
  const [data, setData] = useState([]);
  const [year, setYear] = useState(2025);
  const [loading, setLoading] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [form] = Form.useForm();

  const loadData = useCallback(() => {
    setLoading(true);
    fetch(`${API}/scores?year=${year}&limit=500`)
      .then(r => r.json())
      .then(setData)
      .catch(() => message.error('加载失败'))
      .finally(() => setLoading(false));
  }, [year]);

  useEffect(() => { loadData(); }, [loadData]);

  const openNew = () => { setEditingId(null); form.resetFields(); form.setFieldsValue({ year }); setModalOpen(true); };
  const openEdit = (record) => { setEditingId(record.id); form.setFieldsValue(record); setModalOpen(true); };

  const handleSave = async () => {
    try {
      const values = await form.validateFields();
      const method = editingId ? 'PUT' : 'POST';
      const url = editingId ? `${API}/scores/${editingId}` : `${API}/scores`;
      const resp = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(values),
      });
      if (resp.ok) {
        message.success(editingId ? '已更新' : '已添加');
        setModalOpen(false);
        loadData();
      } else {
        const e = await resp.json();
        message.error(e.detail || '保存失败');
      }
    } catch (e) { /* validation error */ }
  };

  const handleDelete = async (id) => {
    await fetch(`${API}/scores/${id}`, { method: 'DELETE' });
    message.success('已删除');
    loadData();
  };

  const handleBatchImport = async (file) => {
    const text = await file.text();
    const lines = text.trim().split('\n');
    const headers = lines[0].split(',').map(h => h.trim());
    const rows = lines.slice(1).map(line => {
      const vals = line.split(',');
      const row = {};
      headers.forEach((h, i) => { row[h] = vals[i]?.trim(); });
      return row;
    });
    try {
      const resp = await fetch(`${API}/batch-import`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ table: 'scores', rows, year }),
      });
      const result = await resp.json();
      message.success(`导入完成: ${result.ok} 成功, ${result.fail} 失败`);
      loadData();
    } catch (e) { message.error('导入失败'); }
    return false;
  };

  const columns = [
    { title: '院校', dataIndex: 'university_name', width: 140, fixed: 'left',
      onCell: (r) => ({ onClick: () => openEdit(r), style: { cursor: 'pointer' }}) },
    { title: '年份', dataIndex: 'year', width: 70 },
    { title: '专业', dataIndex: 'major_category', width: 130,
      onCell: (r) => ({ onClick: () => openEdit(r), style: { cursor: 'pointer' }}) },
    { title: '专业代码', dataIndex: 'major_code', width: 90 },
    { title: '招生人数', dataIndex: 'enrollment_count', width: 80 },
    { title: '最高分', dataIndex: 'max_score', width: 80 },
    { title: '最低分', dataIndex: 'min_score', width: 80 },
    { title: '平均分', dataIndex: 'avg_score', width: 80 },
    { title: '最低位次', dataIndex: 'min_rank', width: 90 },
    { title: '备注', dataIndex: 'notes', width: 120, ellipsis: true },
    {
      title: '操作', width: 80, fixed: 'right',
      render: (_, r) => (
        <Popconfirm title="确认删除？" onConfirm={() => handleDelete(r.id)}>
          <Button danger size="small" icon={<DeleteOutlined />} />
        </Popconfirm>
      )
    },
  ];

  return (
    <div>
      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col>
          <Select value={year} onChange={setYear}>
            <Select.Option value={2024}>2024年</Select.Option>
            <Select.Option value={2025}>2025年</Select.Option>
            <Select.Option value={2026}>2026年</Select.Option>
          </Select>
        </Col>
        <Col>
          <Button type="primary" icon={<PlusOutlined />} onClick={openNew}>新增</Button>
        </Col>
        <Col>
          <Upload accept=".csv" showUploadList={false} beforeUpload={handleBatchImport}>
            <Button icon={<UploadOutlined />}>批量导入CSV</Button>
          </Upload>
        </Col>
        <Col>
          <Button icon={<DownloadOutlined />} onClick={() => {
            const head = 'university_id,university_name,major_category,major_code,enrollment_count,max_score,min_score,avg_score,min_rank,notes';
            const csv = head + '\n' + data.map(r => [r.university_id,r.university_name,r.major_category,r.major_code,r.enrollment_count,r.max_score,r.min_score,r.avg_score,r.min_rank,r.notes].join(',')).join('\n');
            const blob = new Blob([csv], { type: 'text/csv' });
            const a = document.createElement('a');
            a.href = URL.createObjectURL(blob); a.download = `scores_${year}.csv`; a.click();
          }}>导出CSV</Button>
        </Col>
        <Col><span style={{ lineHeight: '32px', color: '#888' }}>{data.length} 条</span></Col>
      </Row>

      <Table dataSource={data} columns={columns} rowKey="id" size="small"
        scroll={{ x: 1100 }} pagination={{ pageSize: 30 }} loading={loading} />

      <Modal title={editingId ? '编辑录取分数' : '新增录取分数'} open={modalOpen}
        onOk={handleSave} onCancel={() => setModalOpen(false)} width={640}>
        <Form form={form} layout="vertical">
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item label="院校" name="university_id" rules={[{ required: true }]}>
                <Select showSearch placeholder="选择院校"
                  filterOption={(input, option) => option.children.toLowerCase().includes(input.toLowerCase())}>
                  {universities.map(u => (
                    <Select.Option key={u.id} value={u.id}>{u.name}</Select.Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item label="院校名称" name="university_name" rules={[{ required: true }]}>
                <Input placeholder="自动填充" />
              </Form.Item>
            </Col>
          </Row>
          <Row gutter={16}>
            <Col span={6}>
              <Form.Item label="年份" name="year" rules={[{ required: true }]}>
                <Input type="number" />
              </Form.Item>
            </Col>
            <Col span={9}>
              <Form.Item label="专业大类" name="major_category" rules={[{ required: true }]}>
                <Input placeholder="如：计算机类" />
              </Form.Item>
            </Col>
            <Col span={9}>
              <Form.Item label="专业代码" name="major_code">
                <Input placeholder="如：0809" />
              </Form.Item>
            </Col>
          </Row>
          <Row gutter={16}>
            <Col span={6}>
              <Form.Item label="招生人数" name="enrollment_count"><Input type="number" /></Form.Item>
            </Col>
            <Col span={6}>
              <Form.Item label="最高分" name="max_score"><Input type="number" /></Form.Item>
            </Col>
            <Col span={6}>
              <Form.Item label="最低分" name="min_score" rules={[{ required: true }]}><Input type="number" /></Form.Item>
            </Col>
            <Col span={6}>
              <Form.Item label="平均分" name="avg_score"><Input type="number" /></Form.Item>
            </Col>
          </Row>
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item label="最低位次" name="min_rank"><Input type="number" /></Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item label="备注" name="notes"><Input /></Form.Item>
            </Col>
          </Row>
        </Form>
      </Modal>
    </div>
  );
}

// ======================== 一分一段录入 ========================
function SegmentEntry() {
  const [data, setData] = useState([]);
  const [year, setYear] = useState(2026);
  const [loading, setLoading] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [form] = Form.useForm();

  const loadData = useCallback(() => {
    setLoading(true);
    fetch(`${API}/segments?year=${year}&limit=500`)
      .then(r => r.json())
      .then(setData)
      .catch(() => message.error('加载失败'))
      .finally(() => setLoading(false));
  }, [year]);

  useEffect(() => { loadData(); }, [loadData]);

  const openNew = () => { setEditingId(null); form.resetFields(); form.setFieldsValue({ year }); setModalOpen(true); };
  const openEdit = (r) => { setEditingId(r.id); form.setFieldsValue(r); setModalOpen(true); };

  const handleSave = async () => {
    try {
      const values = await form.validateFields();
      const method = editingId ? 'PUT' : 'POST';
      const url = editingId ? `${API}/segments/${editingId}` : `${API}/segments`;
      const resp = await fetch(url, {
        method, headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(values),
      });
      if (resp.ok) { message.success(editingId ? '已更新' : '已添加'); setModalOpen(false); loadData(); }
      else { const e = await resp.json(); message.error(e.detail || '失败'); }
    } catch (e) { /* ok */ }
  };

  const handleDelete = async (id) => { await fetch(`${API}/segments/${id}`, { method: 'DELETE' }); message.success('已删除'); loadData(); };

  const handleBatchImport = async (file) => {
    const text = await file.text();
    const lines = text.trim().split('\n');
    const headers = lines[0].split(',').map(h => h.trim());
    const rows = lines.slice(1).map(line => {
      const vals = line.split(',');
      const row = {};
      headers.forEach((h, i) => { row[h] = vals[i]?.trim(); });
      return row;
    });
    const resp = await fetch(`${API}/batch-import`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ table: 'segments', rows, year }),
    });
    const result = await resp.json();
    message.success(`${result.ok} 成功, ${result.fail} 失败`);
    loadData();
    return false;
  };

  const columns = [
    { title: '年份', dataIndex: 'year', width: 80 },
    { title: '分数', dataIndex: 'score', width: 100, sorter: (a, b) => a.score - b.score,
      onCell: (r) => ({ onClick: () => openEdit(r), style: { cursor: 'pointer' }}) },
    { title: '同分人数', dataIndex: 'count', width: 100 },
    { title: '累计人数', dataIndex: 'cumulative_count', width: 120 },
    { title: '备注', dataIndex: 'notes', width: 120 },
    { title: '来源', dataIndex: 'data_source', width: 100 },
    {
      title: '操作', width: 80,
      render: (_, r) => (
        <Popconfirm title="确认删除？" onConfirm={() => handleDelete(r.id)}>
          <Button danger size="small" icon={<DeleteOutlined />} />
        </Popconfirm>
      )
    },
  ];

  return (
    <div>
      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col>
          <Select value={year} onChange={setYear}>
            <Select.Option value={2024}>2024年</Select.Option>
            <Select.Option value={2025}>2025年</Select.Option>
            <Select.Option value={2026}>2026年</Select.Option>
          </Select>
        </Col>
        <Col><Button type="primary" icon={<PlusOutlined />} onClick={openNew}>新增</Button></Col>
        <Col>
          <Upload accept=".csv" showUploadList={false} beforeUpload={handleBatchImport}>
            <Button icon={<UploadOutlined />}>批量导入CSV</Button>
          </Upload>
        </Col>
        <Col><span style={{ lineHeight: '32px', color: '#888' }}>{data.length} 条</span></Col>
      </Row>

      <Table dataSource={data} columns={columns} rowKey="id" size="small"
        pagination={{ pageSize: 30 }} loading={loading} />

      <Modal title={editingId ? '编辑一分一段' : '新增一分一段'} open={modalOpen}
        onOk={handleSave} onCancel={() => setModalOpen(false)}>
        <Form form={form} layout="vertical">
          <Row gutter={16}>
            <Col span={8}><Form.Item label="年份" name="year" rules={[{ required: true }]}><Input type="number" /></Form.Item></Col>
            <Col span={8}><Form.Item label="分数" name="score" rules={[{ required: true }]}><Input type="number" /></Form.Item></Col>
            <Col span={8}><Form.Item label="同分人数" name="count" rules={[{ required: true }]}><Input type="number" /></Form.Item></Col>
          </Row>
          <Form.Item label="累计人数" name="cumulative_count" rules={[{ required: true }]}>
            <Input type="number" />
          </Form.Item>
          <Row gutter={16}>
            <Col span={12}><Form.Item label="备注" name="notes"><Input /></Form.Item></Col>
            <Col span={12}><Form.Item label="数据来源" name="data_source"><Input /></Form.Item></Col>
          </Row>
        </Form>
      </Modal>
    </div>
  );
}

// ======================== 院校管理 ========================
function UniversityEntry() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [form] = Form.useForm();

  const loadData = useCallback(() => {
    setLoading(true);
    fetch(`${API}/universities-list`)
      .then(r => r.json())
      .then(setData)
      .catch(() => message.error('加载失败'))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => { loadData(); }, [loadData]);

  const openNew = () => { setEditingId(null); form.resetFields(); setModalOpen(true); };
  const openEdit = (r) => { setEditingId(r.id); form.setFieldsValue(r); setModalOpen(true); };

  const handleSave = async () => {
    try {
      const values = await form.validateFields();
      const method = editingId ? 'PUT' : 'POST';
      const url = editingId ? `${API}/universities/${editingId}` : `${API}/universities`;
      if (!editingId) values.id = values.id?.toLowerCase().replace(/\s+/g, '');
      const resp = await fetch(url, {
        method, headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(values),
      });
      if (resp.ok) { message.success(editingId ? '已更新' : '已添加'); setModalOpen(false); loadData(); }
      else { const e = await resp.json(); message.error(e.detail || '失败'); }
    } catch (e) { /* ok */ }
  };

  const handleDelete = async (id) => {
    await fetch(`${API}/universities/${id}`, { method: 'DELETE' });
    message.success('已删除');
    loadData();
  };

  const columns = [
    { title: 'ID', dataIndex: 'id', width: 120,
      onCell: (r) => ({ onClick: () => openEdit(r), style: { cursor: 'pointer' }}) },
    { title: '名称', dataIndex: 'name', width: 160 },
    {
      title: '层次', dataIndex: 'level', width: 80,
      render: (v) => <Tag color={v === '985' ? 'gold' : v === '211' ? 'blue' : v === '双一流' ? 'cyan' : 'default'}>{v}</Tag>
    },
    { title: '省份', dataIndex: 'province', width: 80 },
    { title: '城市', dataIndex: 'city', width: 80 },
    { title: '招生方式', dataIndex: 'admission_mode', width: 120 },
    { title: '官网', dataIndex: 'website', width: 200, ellipsis: true, render: v => v ? <a href={v}>{v}</a> : '' },
    {
      title: '操作', width: 80,
      render: (_, r) => (
        <Popconfirm title="删除院校将同时删除其所有录取数据，确认？" onConfirm={() => handleDelete(r.id)}>
          <Button danger size="small" icon={<DeleteOutlined />} />
        </Popconfirm>
      )
    },
  ];

  return (
    <div>
      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col><Button type="primary" icon={<PlusOutlined />} onClick={openNew}>新增院校</Button></Col>
        <Col><span style={{ lineHeight: '32px', color: '#888' }}>{data.length} 所</span></Col>
      </Row>

      <Table dataSource={data} columns={columns} rowKey="id" size="small"
        pagination={{ pageSize: 50 }} loading={loading} />

      <Modal title={editingId ? '编辑院校' : '新增院校'} open={modalOpen}
        onOk={handleSave} onCancel={() => setModalOpen(false)}>
        <Form form={form} layout="vertical">
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item label="ID（英文缩写）" name="id" rules={[{ required: true }]}>
                <Input disabled={!!editingId} placeholder="如：tsinghua" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item label="名称" name="name" rules={[{ required: true }]}>
                <Input placeholder="如：清华大学" />
              </Form.Item>
            </Col>
          </Row>
          <Row gutter={16}>
            <Col span={8}><Form.Item label="层次" name="level"><Select allowClear>
              <Select.Option value="985">985</Select.Option>
              <Select.Option value="211">211</Select.Option>
              <Select.Option value="双一流">双一流</Select.Option>
              <Select.Option value="普通">普通</Select.Option>
            </Select></Form.Item></Col>
            <Col span={8}><Form.Item label="省份" name="province"><Input /></Form.Item></Col>
            <Col span={8}><Form.Item label="城市" name="city"><Input /></Form.Item></Col>
          </Row>
          <Form.Item label="招生方式" name="admission_mode"><Input placeholder="如：统招/综合评价" /></Form.Item>
          <Form.Item label="官网" name="website"><Input placeholder="https://..." /></Form.Item>
        </Form>
      </Modal>
    </div>
  );
}

// ======================== 招生计划录入 ========================
function BPlanEntry({ universities }) {
  const [data, setData] = useState([]);
  const [year, setYear] = useState(2026);
  const [loading, setLoading] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [form] = Form.useForm();

  const loadData = useCallback(() => {
    setLoading(true);
    fetch(`${API}/plans?year=${year}&limit=500`)
      .then(r => r.json())
      .then(setData)
      .catch(() => message.error('加载失败'))
      .finally(() => setLoading(false));
  }, [year]);

  useEffect(() => { loadData(); }, [loadData]);

  const openNew = () => { setEditingId(null); form.resetFields(); form.setFieldsValue({ year }); setModalOpen(true); };
  const openEdit = (r) => { setEditingId(r.id); form.setFieldsValue(r); setModalOpen(true); };

  const handleSave = async () => {
    try {
      const values = await form.validateFields();
      const method = editingId ? 'PUT' : 'POST';
      const url = editingId ? `${API}/plans/${editingId}` : `${API}/plans`;
      const resp = await fetch(url, {
        method, headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(values),
      });
      if (resp.ok) { message.success(editingId ? '已更新' : '已添加'); setModalOpen(false); loadData(); }
      else { const e = await resp.json(); message.error(e.detail || '失败'); }
    } catch (e) { /* ok */ }
  };

  const handleDelete = async (id) => { await fetch(`${API}/plans/${id}`, { method: 'DELETE' }); message.success('已删除'); loadData(); };

  const handleBatchImport = async (file) => {
    const text = await file.text();
    const lines = text.trim().split('\n');
    const headers = lines[0].split(',').map(h => h.trim());
    const rows = lines.slice(1).map(line => {
      const vals = line.split(',');
      const row = {};
      headers.forEach((h, i) => { row[h] = vals[i]?.trim(); });
      return row;
    });
    try {
      const resp = await fetch(`${API}/batch-import`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ table: 'plans', rows, year }),
      });
      const result = await resp.json();
      message.success(`导入完成: ${result.ok} 成功, ${result.fail} 失败`);
      loadData();
    } catch (e) { message.error('导入失败'); }
    return false;
  };

  const columns = [
    { title: '院校', dataIndex: 'university_name', width: 140, fixed: 'left',
      onCell: (r) => ({ onClick: () => openEdit(r), style: { cursor: 'pointer' }}) },
    { title: '年份', dataIndex: 'year', width: 70 },
    { title: '专业代号', dataIndex: 'major_code', width: 90 },
    { title: '专业组序号', dataIndex: 'major_group_sequence', width: 100 },
    { title: '专业大类', dataIndex: 'major_category', width: 130,
      onCell: (r) => ({ onClick: () => openEdit(r), style: { cursor: 'pointer' }}) },
    { title: '选考科目', dataIndex: 'required_subjects', width: 90 },
    { title: '招生人数', dataIndex: 'enrollment_count', width: 80 },
    { title: '学费', dataIndex: 'tuition', width: 80 },
    { title: '校区', dataIndex: 'campus', width: 80 },
    { title: '数据来源', dataIndex: 'data_source', width: 100, ellipsis: true },
    {
      title: '操作', width: 80, fixed: 'right',
      render: (_, r) => (
        <Popconfirm title="确认删除？" onConfirm={() => handleDelete(r.id)}>
          <Button danger size="small" icon={<DeleteOutlined />} />
        </Popconfirm>
      )
    },
  ];

  return (
    <div>
      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col>
          <Select value={year} onChange={setYear}>
            <Select.Option value={2024}>2024年</Select.Option>
            <Select.Option value={2025}>2025年</Select.Option>
            <Select.Option value={2026}>2026年</Select.Option>
          </Select>
        </Col>
        <Col><Button type="primary" icon={<PlusOutlined />} onClick={openNew}>新增</Button></Col>
        <Col>
          <Upload accept=".csv" showUploadList={false} beforeUpload={handleBatchImport}>
            <Button icon={<UploadOutlined />}>批量导入CSV</Button>
          </Upload>
        </Col>
        <Col>
          <Button icon={<DownloadOutlined />} onClick={() => {
            const head = 'university_id,university_name,major_code,major_group_sequence,major_group_name,required_subjects,major_category,included_majors,tuition,enrollment_count,campus,notes,data_source';
            const csv = head + '\n' + data.map(r => [r.university_id,r.university_name,r.major_code,r.major_group_sequence,r.major_group_name,r.required_subjects,r.major_category,(r.included_majors||'').replace(/,/g,';'),r.tuition,r.enrollment_count,r.campus,r.notes,r.data_source].join(',')).join('\n');
            const blob = new Blob([csv], { type: 'text/csv' });
            const a = document.createElement('a');
            a.href = URL.createObjectURL(blob); a.download = `plans_${year}.csv`; a.click();
          }}>导出CSV</Button>
        </Col>
        <Col><span style={{ lineHeight: '32px', color: '#888' }}>{data.length} 条</span></Col>
      </Row>

      <Table dataSource={data} columns={columns} rowKey="id" size="small"
        scroll={{ x: 1200 }} pagination={{ pageSize: 30 }} loading={loading} />

      <Modal title={editingId ? '编辑招生计划' : '新增招生计划'} open={modalOpen}
        onOk={handleSave} onCancel={() => setModalOpen(false)} width={720}>
        <Form form={form} layout="vertical">
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item label="院校" name="university_id" rules={[{ required: true }]}>
                <Select showSearch placeholder="选择院校"
                  filterOption={(input, option) => option.children.toLowerCase().includes(input.toLowerCase())}>
                  {universities.map(u => (
                    <Select.Option key={u.id} value={u.id}>{u.name}</Select.Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item label="院校名称" name="university_name" rules={[{ required: true }]}>
                <Input placeholder="自动填充" />
              </Form.Item>
            </Col>
          </Row>
          <Row gutter={16}>
            <Col span={6}>
              <Form.Item label="年份" name="year" rules={[{ required: true }]}><Input type="number" /></Form.Item>
            </Col>
            <Col span={9}>
              <Form.Item label="专业代号" name="major_code" rules={[{ required: true }]}><Input placeholder="如：01" /></Form.Item>
            </Col>
            <Col span={9}>
              <Form.Item label="专业组序号" name="major_group_sequence"><Input placeholder="如：01" /></Form.Item>
            </Col>
          </Row>
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item label="专业组名称" name="major_group_name"><Input /></Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item label="选考科目" name="required_subjects"><Input placeholder="如：化学" /></Form.Item>
            </Col>
          </Row>
          <Form.Item label="专业大类" name="major_category" rules={[{ required: true }]}>
            <Input placeholder="如：计算机类" />
          </Form.Item>
          <Form.Item label="包含专业" name="included_majors">
            <Input.TextArea rows={2} placeholder='JSON数组格式，如：["计算机科学与技术","软件工程"]' />
          </Form.Item>
          <Row gutter={16}>
            <Col span={6}>
              <Form.Item label="学费" name="tuition"><Input type="number" /></Form.Item>
            </Col>
            <Col span={6}>
              <Form.Item label="招生人数" name="enrollment_count"><Input type="number" /></Form.Item>
            </Col>
            <Col span={6}>
              <Form.Item label="校区" name="campus"><Input /></Form.Item>
            </Col>
            <Col span={6}>
              <Form.Item label="数据来源" name="data_source"><Input placeholder="如：官方招生计划" /></Form.Item>
            </Col>
          </Row>
          <Form.Item label="备注" name="notes"><Input /></Form.Item>
        </Form>
      </Modal>
    </div>
  );
}

export default DataEntry;
